# Reddit Post Downloader
A web scraper-based python Reddit post downloader that works in 2023. 

## Table of Contents
- [Introduction](#introduction)
  - [Background](#background)
- [Installation](#installation)
  - [Reddit Post Downloader command-line utility](#command_line_tool)
  - [Reddit Link Grabber Chrome browser extension](#browser_extension)

- [How to Use Command-Line Tool](#command_line_how_to)
- [How to Use Browser Extension](#browser_extension_how_to)
- [Conclusion](#conclusion)

# Introduction <a id="introduction"></a>
Reddit Post Downloader is a command-line utility for downloading reddit posts. Included is also an optional Chrome browser extension, the Reddit Link Grabber, to help gather links from Reddit itself.

### Backround <a id=background></a>
I used to use [aliparlacki's BDFR tool](https://github.com/aliparlakci/bulk-downloader-for-reddit) for downloading reddit posts but after the Reddit API changes, I noticed a lot of rate limiting errors.

This tool uses web scraping to download the posts and therefore doesn't trigger the Reddit API rate-limiting. It isn't anywhere near as fast as BDFR was, but it still works as of July 2023.

In testing, I decided I needed a Chrome extension to help grab links from Reddit itself. While optional, the Reddit Link Grabber extension is very helpful at piping links into the utility for downloading.

## Installation <a id="installation"></a>
Python >=3.9 is required

### Reddit Post Downloader command-line utility <a id="command_line_tool"></a>
#### Option 1: Cloning the Repo and installing the tool.
- Step 1: Open a terminal or command prompt.
- Step 2: Change to the directory where you'd like to store the Reddit Post Downloader tool.
- Step 3: Clone the repository using the following command:

  ```
  git clone https://github.com/eric_hamilton/reddit_post_downloader.git
  ```

- step 4: Extract the .zip file and enter the repository directory.
- step 5: Install the requirements for the utility unsing:

  ```
  python setup.py install
  ```
- Finished. This will add the Reddit Post Downloader to your system path and it will be runnable using the `rdu` command.

#### Option 2: Download the release package
  - Under releases, grab the latest 'reddit_post_downloader.exe'
  - Feel free to verify the executable using the provided 'reddit_post_downloader.sha256'
  - Navigate to the directory with the executable and open a command prompt or terminal
  - Use the executable just like the command line tool, just use `reddit_post_downloader.exe` instead of `rdu`
  - For more examples, see [How to Use Command-Line Tool](#command_line_how_to)

### Reddit Link Grabber Chrome browser extension (optional) <a id="browser_extension"></a>

1. **Download the extension files**:
   - Go to the repository's releases page: [Reddit Post Downloader Releases](https://github.com/eric_hamilton/reddit_post_downloader/releases).
   - Download the latest release zip file that includes the Chrome extension.

2. **Extract the extension files**:
   - Once the zip file is downloaded, extract its contents to a location of your choice.

3. **Install the extension in Chrome**:
   - Open the Chrome browser.
   - In the address bar, type `chrome://extensions/` and press Enter.
   - Enable "Developer mode" by toggling the switch in the top right corner.

4. **Load the extension**:
   - Click on the "Load unpacked" button in the top left corner.
   - Browse to the location where you extracted the extension files and select the folder containing the extension.

5. **Confirm the installation**:
   - The Reddit Link Grabber extension should now appear in the list of installed extensions.
   - Make sure the "Enabled" box is checked next to the extension to activate it.

6. **Verify the extension**:
   - Go to a Reddit page in Chrome, and you should see the Reddit Link Grabber icon in the Chrome toolbar.

The Reddit Link Grabber extension is now installed and ready to use. It will help you gather links from Reddit pages for use with the Reddit Post Downloader utility.

## How to Use Command-Line Utility <a id="command_line_how_to"></a>

1. **Running Commands**:
   - Once the utility is installed, you can run the Reddit Post Downloader using the `rdu` command in your terminal or command prompt.
   
   ```
   rdu [options]
   ```
2. **Command-Line Options**:
   - The Reddit Post Downloader provides several options to download Reddit posts:
     - `-s` or `--subreddit`:  Get the top posts of a specific subreddit.
     - `-p` or `--post`: Download a single post by providing its permalink.
     - `-f` or `--file`: Provide a text file containing links to download multiple posts.
     - `-w` or `--web`: Download a list of links copied via the Reddit Link Grabber Chrome extension.
     - `-r` or `--range`: Specify the time range for searching subreddit posts (hour, day, week, month, year, or all).
     - `-c` or `--category`: Specify the category for searching subreddit posts (new, hot, rising, controversial, or top).
     - `-l` or `--limit`: Set the limit of top posts to download (default is 10).
     - `-o` or `--output`: Specify the output folder path where the downloaded posts will be saved (default is "output").

3. **Examples**:
   - Download the top 5 posts from the "python" subreddit:
     
     ```
     rdu -s python -l 5
     ```
     
   - Download a specific post using its permalink:
     
     ```
     rdu -p https://www.reddit.com/r/some_subreddit/comments/post_id/post_title/
     ```
     
   - Download posts from a text file containing multiple links:
     
     ```
     rdu -f path/to/links.txt
     ```
     
   - Download posts from links copied to the clipboard via the RDU Chrome extension (or just properly formatted links in the clipboard)
     
     ```
     rdu -w
     ```
     
## How to Use Browser Extension <a id="browser_extension_how_to"></a>

The Reddit Link Grabber Chrome extension is designed to help you grab links to Reddit posts on a given page. Follow these steps to use the extension:

### Copy all links on page to clipboard:
  - Simply click on the extension icon and the extension will copy all of the links it finds on the page to the clipboard. Note: clicking the icon will clear the clipboard first.
  - You can also right click on the page to show the context menu. Hover over "Reddit Link Grabber" and choose how you'd like to grab your links.

### Add a single link to clipboard:
  - By right-clicking on a link to a post, you'll see the context menu appear. By hovering over "Reddit Link Grabber," you should see the option to add a link to the clipboard. You can choose to clear the clipboard first or add to it.

Please note that the Reddit Link Grabber extension is designed to work on pages with Reddit links, and it will only grab valid links. Additionally, the extension may not work on certain pages due to restrictions or changes on the Reddit website.

# Conclusion <a id="conclusion"></a>
Reddit may make another change that prohibits even this methodology for downloading posts, but this should be the lowest common denominator for the forseeable future. Until they start obfuscating their html any further or remove .json entirely.
