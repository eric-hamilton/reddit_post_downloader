import os
import tempfile
import argparse
import requests
import json
import time
import re
import pyperclip
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from moviepy.editor import VideoFileClip, AudioFileClip

import chromedriver_autoinstaller

chromedriver_autoinstaller.install()


def sanitize_filename(filename):
    # Get rid of non Windows path safe characters
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized_filename = re.sub(r'[{}]'.format(re.escape(''.join(forbidden_chars))), '_', filename)

    if not sanitized_filename.strip():
        sanitized_filename = 'Untitled'

    sanitized_filename = sanitized_filename.strip('. ').rstrip()
    max_length = 255
    if len(sanitized_filename) > max_length:
        sanitized_filename = sanitized_filename[:max_length]
    return sanitized_filename


def is_valid_reddit_link(link):
    reddit_link_pattern = r'https?://(?:www\.)?reddit\.com/r/[a-zA-Z0-9_]+/comments/[a-zA-Z0-9_]+/?'    
    return re.match(reddit_link_pattern, link)


def verify_reddit_links_in_clipboard(clipboard_content):
    if not clipboard_content:
        return False
    valid_links = set()
    for line in clipboard_content.split("\n"):
        link = line.strip()
        if not is_valid_reddit_link(link):
            return False
        else:
            valid_links.add(link)
    return valid_links


def verify_reddit_links_in_file(file_path):
    if not os.path.isfile(file_path):
        return False
    valid_links = set()
    with open(file_path, 'r') as file:
        for line in file:
            link = line.strip()
            if not is_valid_reddit_link(link):
                return False
            else:
                valid_links.add(link)

    return valid_links


def find_key_recursively(data, target_key):
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        else:
            for value in data.values():
                result = find_key_recursively(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursively(item, target_key)
            if result is not None:
                return result
    return None


def merge_video_and_audio(vid_link, aud_link, output_filename):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_video_file = os.path.join(temp_dir, 'temp_video.mp4')
        temp_audio_file = os.path.join(temp_dir, 'temp_audio.mp3')

        video_clip = VideoFileClip(vid_link)
        audio_clip = None

        try:
            # The audio link is programatically generated because reddit doesn't provide one.
            # Some videos don't have audio. Just try/error through it.
            if aud_link:
                audio_clip = AudioFileClip(aud_link)
                audio_clip.write_audiofile(temp_audio_file)
        except Exception as e:
            traceback.print_exc()
            print(f"Error loading audio: {e}")

        if audio_clip:
            final_clip = video_clip.set_audio(audio_clip)
        else:
            final_clip = video_clip

        final_clip.write_videofile(temp_video_file, codec="libx264", verbose=False)

        # Unnecessarily convoluted way of avoiding duplicate filenames
        try:
            os.rename(temp_video_file, output_filename)
        except FileExistsError as e:
            suffix = 1
            while True:
                new_output_filename = f"{output_filename}_({suffix}))"
                try:
                    os.rename(temp_video_file, new_output_filename)
                    break 
                except FileExistsError:
                    suffix += 1

        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)


def save_post(post_data, base_output_folder):

    # take the sub and post names from the permalink because it's more nicely formatted
    link_parts = post_data['permalink'].split("/")
    subreddit_name = link_parts[2]
    post_id = link_parts[4]
    post_title = link_parts[5]

    output_directory = os.path.join(base_output_folder, subreddit_name, post_id+"_"+post_title)
    os.makedirs(output_directory, exist_ok=True)

    if post_data["is_video"]:
        media_link = find_key_recursively(post_data, "fallback_url")
        if media_link:
            media_link = media_link.replace("?source=fallback", "")
        else:
            media_link = ""

        if media_link.lower().endswith(".mp4"):
            audio_pattern = r"DASH_.*?\.mp4"
            audio_link = re.sub(audio_pattern, "DASH_audio.mp4", media_link)

            filename = sanitize_filename(f"{post_title}.mp4")
            output_path = os.path.join(output_directory, filename)
            merge_video_and_audio(media_link, audio_link, output_path)
            return

    metadata = post_data.get("media_metadata")
    if metadata:
        for i, x in enumerate(metadata):
            output_filename = f"{post_title}_{i+1}.jpg"
            output_filename = sanitize_filename(output_filename)
            output_path = os.path.join(output_directory, output_filename)
            image_url = metadata[x]["s"]["u"]

            image_url = image_url.replace('&amp;', '&')
            response = requests.get(image_url)

            if response.status_code == 200:
                with open(output_path, 'wb') as file:
                    file.write(response.content)
                print(f"Image {i+1} of {len(metadata)} downloaded successfully.")
                time.sleep(0.5) # avoid rate limiting
            else:
                print(response.status_code)
                print(f"{output_filename} failed to download")
        return

    preview = post_data.get("preview")
    if preview:
        images = preview.get("images")
        if images:
            for i, image in enumerate(images):
                output_filename = f"{post_title}_{i+1}.jpg"
                output_filename = sanitize_filename(output_filename)
                output_path = os.path.join(output_directory, output_filename)
                image_url = image["source"]["url"].replace('&amp;', '&')
                response = requests.get(image_url)

                if response.status_code == 200:
                    with open(output_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Image {i+1} of {len(images)} downloaded successfully.")
                    time.sleep(0.5) # avoid rate limiting
                else:
                    print(response.status_code)
                    print(f"{output_filename} failed to download")
            

def get_posts_on_page(page_data):
    post_data_list = []
    for child in page_data.get("children", []):
        post_data_list.append(child["data"])
    last_id = page_data.get("after")
    return post_data_list, last_id


def get_posts(subreddit, driver, limit, sort_category, sort_range):
    post_data_list = []

    url = f"https://www.reddit.com/r/{subreddit}/{sort_category}/.json?t={sort_range}"

    searching = True
    fail_count = 0
    fail_limit = 5
    sleep_time = 5 # seconds
    last_count = len(post_data_list)
    after_id = None # How reddit API handles pagination

    while searching:
        try:
            new_url = url
            if after_id:
                new_url += f"&after={after_id}"

            driver.get(new_url)
            data_str = driver.find_element(By.TAG_NAME, 'pre').text
            data = json.loads(data_str)
            page_data = data.get("data")

            if page_data is None:
                # No more data to fetch, break out of the loop
                break

            new_post_data, after_id = get_posts_on_page(page_data)
            post_data_list.extend(new_post_data)

            current_count = len(post_data_list)
            if limit != 0:
                if current_count >= limit:
                    post_data_list = post_data_list[:limit]
                    driver.quit()
                    print(f"{len(post_data_list)} posts found! Saving...")
                    return post_data_list 

            if current_count == last_count:
                # Increment this count for each page that is checked where no new data is grabbed
                # Can occur when subreddit doesn't have as many posts as the set limit
                fail_count += 1
                print(f"Failed to find new posts: {fail_count}/{fail_limit}")

            if fail_count > fail_limit:
                searching = False
            else:
                print(f"Found {len(new_post_data)} new posts. Total: {current_count}. Sleeping {sleep_time} seconds.")
                time.sleep(sleep_time)
            last_count = current_count
        except Exception as e:
            traceback.print_exc()
            print(e)
            searching = False

    driver.quit()
    print(f"{len(post_data_list)} posts found! Saving...")
    return post_data_list


def validate_args(args):
    arg_count = sum(arg is not None and arg is not False for arg in [args.subreddit, args.post, args.file, args.web])
    if arg_count > 1:
        raise argparse.ArgumentTypeError("Only one of -s, -p, -f, or -w can be specified")
    elif arg_count == 0:
        raise argparse.ArgumentTypeError("Missing download argument: (-s, -p, -f, or -w required)")

def main():
    parser = argparse.ArgumentParser(description="Download Reddit posts.")
    parser.add_argument("-s", "--subreddit", required=False, help="Get the top posts of a subreddit")
    parser.add_argument("-p", "--post", help="Download a single post by providing its permalink")
    parser.add_argument("-f", "--file", help="Provide a text file of links to download")
    parser.add_argument("-w", "--web", action="store_true", help="Download a list of links copied via Reddit Link Grabber")
    parser.add_argument("-r", "--range",
            choices=['hour', 'day', 'week', 'month', 'year', 'all'],
            default="all", help="What range to search subreddit posts by")

    parser.add_argument("-c", "--category",
            choices=['new', 'hot', 'rising', 'controversial', 'top'],
            default="top", help="What category to search subreddit posts by")

    parser.add_argument("-l", "--limit", type=int, default=10, help="The limit of top posts to download (0 == no limit)")
    parser.add_argument("-o", "--output", default="output", help="The output folder path")

    args = parser.parse_args()
    validate_args(args)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    if args.post:
        try:
            post_url = args.post
            if ".json" not in post_url:
                post_url = post_url+".json"
            driver.get(post_url)
            data_str = driver.find_element(By.TAG_NAME, 'pre').text
            data = json.loads(data_str)[0]
            post_data = data["data"]["children"][0]["data"]
            save_post(post_data, args.output)

        except Exception as e:
            traceback.print_exc()
            print("Failed to download the post.")

    elif args.file:
        file_path = args.file
        valid_links = verify_reddit_links_in_file(file_path)
        if valid_links:
            for link in valid_links:
                try:
                    post_url = link+".json"
                    driver.get(post_url)
                    data_str = driver.find_element(By.TAG_NAME, 'pre').text
                    data = json.loads(data_str)[0]
                    post_data = data["data"]["children"][0]["data"]
                    save_post(post_data, args.output)

                except Exception as e:
                    traceback.print_exc()
                    print("Failed to download the post.")

        else:
            print("Invalid link found or no links given")
            print("link file should be one link per line with no extra characters")

    elif args.web:
        clipboard_content = pyperclip.paste()
        valid_links = verify_reddit_links_in_clipboard(clipboard_content)
        if valid_links:
            for link in valid_links:
                try:
                    post_url = link+".json"
                    driver.get(post_url)
                    data_str = driver.find_element(By.TAG_NAME, 'pre').text
                    data = json.loads(data_str)[0]
                    post_data = data["data"]["children"][0]["data"]
                    save_post(post_data, args.output)

                except Exception as e:
                    traceback.print_exc()
                    print("Failed to download the post.")

        else:
            print("Invalid link found or no links found in clipboard")
            print("Clipboard should contain one reddit link per line")

    elif args.subreddit:
        post_data_list = get_posts(args.subreddit, driver, args.limit, args.category, args.range)

        for i, post_data in enumerate(post_data_list):
            try:
                print(f"\nSaving post {i+1} out of {len(post_data_list)}.\n")
                save_post(post_data, args.output)
            except Exception as e:
                traceback.print_exc()
                print(f"Failed to download {post_data['permalink']}")


if __name__ == "__main__":
    main()
    print("Finished!")
