---
title: Using Python Virtual Environments
description: Managing virtual environments across multiple systems within Arch Linux.
# slug: hello-world
date: 2024-12-02 00:00:01+0000
lastmod: 2024-12-02 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Tech
tags:
    - Python
    - Arch Linux
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Python Module Management

As an Arch Linux user, the push is to utilize pacman and related tools to manage dependencies and package updates (including Python modules). In fact, [the wiki itself](https://wiki.archlinux.org/title/Python) explicitly states this (see 2.1), and the default Arch installation of Python disables python-pip.

Unfortunately, there are limited resources put into maintaining packages for modules and only the most common and popular modules are maintained, and they are updated promptly as is consistent within the Arch ecosystem.

## Creating A Virtual Environment

After recently delving into crypto and the web3 Python module, the Coinbase API, and others, I've found the need to install Python modules from [Pypi](https://pypi.org/), the Python package index. This is the most exhaustive location to find modules, including the latest updates and version history.

Using python-pip necessitated the use of virtual environments, which made me reconsider the idea of not maintaining Python modules (or maintaining very few) through pacman at all.

I chose to place the virtual environments at `~/python-virtual-envs/` and within that directory have one called `general` and other called `wrds`. The `wrds` environment is specific to the [Wharton Research Data Services](https://wrds-www.wharton.upenn.edu/) which requires (for some reason) an older package of nympy.

The "general" environment covers everything else. I created it with the usual command:

    $ python -m venv ~/python-virtual-envs/general

Once created, it can be activated (either in a terminal or an IDE such as VS Code) by executing the following in the terminal:

    $ source ~/python-virtual-envs/general/bin/activate

## Using python-pip

After the virtual environment is created and activated, modules can be installed by using python-pip, such as:

    $ pip install <package-name>

If you want to view all installed modules, run:

    $ pip list

Or the outdated modules:

    $ pip list --outdated

And updated at a later point in time with:

    $ pip install --upgrade <package-name>

## Maintaining Across Multiple Systems

To avoid having to redundantly install modules on different systems, after I make a change to the virtual environment I zip the entire `~/python-virtual-envs/` directory and upload the zip file to Dropbox. This takes less than a minute, and if I am working on a different system can simply extract the archive and have a completely up-to-date and current virtual environment to work in.

## References

https://docs.python.org/3/library/venv.html</br>
https://pypi.org/</br>
https://note.nkmk.me/en/python-pip-usage/</br>
https://wiki.archlinux.org/title/Python