---
title: Hello World
description: Welcome to my website.
slug: hello-world
date: 2023-09-26 00:00:00+0000
lastmod: 2023-12-10 00:00:00+0000
image: cover.jpg
draft: false
categories:
    - Blog
tags:
    - Hugo
    - GitHub
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Hello World

Welcome to my website. This is meant to serve as a place for me to publish various posts from my explorations into Arch Linux, data science, quant finance, and other topics.

The theme has been adopted from the [Hugo Theme Stack](https://github.com/CaiJimmy/hugo-theme-stack) produced by Jimmy Cai.

This is the only theme that I have found that checks all of the following boxes:

* Theme for the static site generator Hugo
* Includes modules for archives
* Includes tags and topics/categories
* Includes built-in search functionality
* Simple interface that is easily navigable
* Highly extensible including modules for image galleries, posts, comment capabilities, etc.

It is hosted on [GitHub pages](https://pages.github.com/). I followed the install instructions that the theme author provided, including using GitHub codespace for editing in the cloud. There are only a few details that I ran into that he did not mention.

1. Don't forget to run Hugo to build the site. This creates the public directory, which is where the static site files are located.
2. Make sure to update the branch to be gh-pages under Settings -> Pages -> Build and deployment -> Branch in GitHub.
3. Make sure to remove the public directory from the .gitignore file. Otherwise GitHub will ignore the public directory and your site will show the README.md instead of the Hugo site.

The site can be updated either through codespace, or locally as long as Hugo and it's required dependencies have been installed.

## Updating and pushing changes

The simple command after making any changes and to push those updates is as follows:

    $ hugo && git add . && git commit -am "Updating site" && git push

This can be put in a bash script to make it easier. Save the following as `git-update.sh`:

```bash
#!/bin/bash
echo What is the commit message?

read message

hugo && git add . && git commit -am "$message" && git push
```

Change permissions:

    $ chmod +x git-update.sh

And then execute:

    $ ./git-update.sh

## References

Here's the full list of resources I referenced for deploying Hugo with GitHub pages:

https://www.o11ycloud.com/posts/gh_hugo/</br>
https://github.com/CaiJimmy/hugo-theme-stack</br>
https://medium.com/@magstherdev/github-pages-hugo-86ae6bcbadd