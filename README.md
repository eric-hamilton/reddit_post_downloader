# Reddit Post Downloader
A web scraper-based python Reddit post downloader that works in 2023. 

## Table of Contents
- [Introduction](#introduction)
  - [Background](#background)
- [Installation](#installation)
  - [Reddit Post Downloader command-line utility](#command_line_tool)
  - [Reddit Link Grabber Chrome browser extension](#browser_extension)
- [How to Use](#how_to_use)
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
### Reddit Link Grabber Chrome browser extension (optional) <a id="browser_extension"></a>

## How to Use <a id="how_to_use"></a>

### Command-Line Utility
### Browser Extension
# Conclusion <a id="conclusion"></a>
Reddit may make another change that prohibits even this methodology for downloading posts, but this should be the lowest common denominator for the forseeable future. Until they start obfuscating their html any further or remove .json entirely.
