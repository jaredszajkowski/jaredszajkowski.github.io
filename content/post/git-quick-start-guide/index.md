---
title: Git Quick Start Guide
description: Commonly used commands and functionality for git.
#slug: hello-world-2
date: 2023-10-16 00:00:00+0000
lastmod: 2023-10-18 00:00:00+0000
# image: cover.jpg
draft: false
categories:
    - Tutorial
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

    $ yay git

Pacman will include all required depencies.

## Initial configuration

First, set your name and email address:

    $ git config --global user.name "Firstname Lastname"
    $ git config --global user.email "email@address.com"

Then, set your preferred text editor (if you have one). I use nano:

    $ git config --global core.editor "nano"

You can verify the updates with:

    $ git config --global core.editor

Alternatively, you can edit the git configuration with:

    $ git config --global --edit

## Store credentials

In 2021, GitHub disabled authentication via username and password, and now requires authentication with a token. The following command sets up the credential helper, where it will store your token in `~/.git-credentials`:

    $ git config --global credential.helper store

After you log in during a push with your username and token, it will be stored in the above location.

Note: The token is stored in plain text, so use caution if that is a concern.

## Cloning repositories

Repositories can be cloned with the following:

    $ git clone https://github.com/<username>/<repository>.git

## Updating repositories

The local record of a repository can be updated with the following command:

    $ cd <repository>/
    $ git pull

## Adding, committing, and pushing

Any files or directories that have been added, modified, or removed can be add to the list of changes to be pushed with the following command:

    $ git add .

Then committed (staged in preparation to push) with the following command:

    $ git commit -am "Add your commit message here"

Note: Without `add`, `commit` will handle any changes to files that have been modified or deleted, but will not incorporate any files that have been created.

Then finally pushed:

    $ git push

If, for some reason, you would like to reset a commit:

    $ git reset

These commands can be chained together with the AND operator:

    $ git add . && git commit -am "Add your commit message here" && git push

## References

References for git (and used for above):

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens</br>
https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup#_first_time</br>
https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config</br>
https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage#_credential_caching</br>
https://www.geeksforgeeks.org/difference-between-chaining-operators-in-linux/