---
title: Using yt-dlp With Zoom
description: Bash script for usage of yt-dlp with Zoom.
#slug: hello-world-2
date: 2023-10-03 00:00:00+0000
lastUpdated: 2023-10-04 00:00:00+0000
# image: cover.jpg
draft: false
categories:
    - Tech
tags:
    - yt-dlp
    - Zoom
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

If anyone uses Zoom to record or access recordings of video calls, here's a simple linux bash script to download the video file and acompanying subtitles.

This requires you to have a "cookies" text file, which needs to contain the cookies export in the Netscape HTTP format of the Zoom cookies after logging in.

Here's the steps to setting this up:

1. Install [cookie editor](https://microsoftedge.microsoft.com/addons/detail/cookie-editor/ajfboaconbpkglpfanbmlfgojgndmhmc).
2. Change preferred export format to `Netscape HTTP Cookie File` in the extension options.
3. Log in to zoom.
4. Export cookies and save to cookies.txt.
5. Save the following code (my bash script file name is yt-dlp.sh):

```html
#!/bin/bash
echo What is the link?

read link

yt-dlp --referer "https://zoom.us/" --cookies /path/to/cookies/file/cookies.txt -o "%(title)s-%(id)s.%(ext)s" --write-subs $link
```

6. Change permissions of the bash script to allow execution:

    $ chmod +x yt-dlp.sh

7. Execute the bash script with ./yt-dlp.sh, copy and paste the link to the video that you would like to save, and it should download the video and the subtitles.