---
title: Git Quick Start Guide
description: Commonly used commands and functionality for git.
#slug: hello-world-2
date: 2023-10-16 00:00:00+0000
lastmod: 2023-10-16 00:00:00+0000
# image: cover.jpg
draft: true
categories:
    - Tech
tags:
    - git
    - GitHub
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

Here are my notes for some of the more commonly used git commands along with initial setup for git in Linux.

## Installation 

To begin, install as follows:

    # pacman -Syu git

Or

    # yay git

Pacman will include all required depencies.

## Initial configuration

Some good first steps.


If anyone uses Zoom to record and later wants to access recordings of video calls, here's a simple linux bash script to download the video file and acompanying subtitles. For a long time I used [zoomdl](https://github.com/Battleman/zoomdl), but it is no longer under active development, and I began running into various issues about a year ago.

This tutorial requires you to have a "cookies" text file, which needs to contain the cookies export in the Netscape HTTP format of the Zoom cookies after logging in.

Here's the steps to setting this up:

## Step 1 - Install [cookie editor](https://microsoftedge.microsoft.com/addons/detail/cookie-editor/ajfboaconbpkglpfanbmlfgojgndmhmc)

I personnally use it with Microsoft Edge, but there are similar extensions for Chrome, Firefox, etc.

## Step 2 - Modify cookie export format

Change preferred export format to `Netscape HTTP Cookie File` in the extension options. It is necessary to export in this format, otherwise yt-dlp will not be able to read the cookies.txt file correctly.

![Modify preferred export format](1.png)

## Step 3 - Log in to Zoom

Log in to Zoom in your browser. Be sure to remain logged in while exporting the cookies under step 4.

## Step 4 - Export cookies and save to cookies.txt

The export button is at the top fo the window. It copies the cookies to your clipboard, which can then be pasted into a text file (I have my saved as cookies.txt).

![Export cookies](2.png)

## Step 5 - Save the following code

Save the following code to a text file (my bash script file name is yt-dlp.sh):

```html
#!/bin/bash
echo What is the link?

read link

yt-dlp --referer "https://zoom.us/" --cookies /path/to/cookies/file/cookies.txt -o "%(title)s-%(id)s.%(ext)s" --write-subs $link
```

## Step 6 - Change permissions

Modify the permissions of the bash script to allow execution:

    $ chmod +x yt-dlp.sh

## Step 7 - Execute the bash script

Execute the bash script with ./yt-dlp.sh, copy and paste the link to the video that you would like to save, and it should download the video and the subtitles.