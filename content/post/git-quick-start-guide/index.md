---
title: Git Quick Start Guide
description: Commonly used commands and functionality for git.
#slug: hello-world-2
date: 2023-10-16 00:00:00+0000
lastmod: 2025-06-10 00:00:00+0000
image: cover.jpg
draft: false
categories:
    - Tech
    - Tutorials
tags:
    - Git
    - GitHub
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Introduction

Here are my notes for some of the more commonly used git commands along with initial setup for git in Linux.

## Installation

To begin, install as follows for Arch Linux:

    $ sudo pacman -Sy git

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

Alternatively, you can edit the git configuration directly with:

    $ git config --global --edit

## Store credentials

In 2021, GitHub disabled authentication via password and now requires authentication with a token. The following command sets up the credential helper, where it will store your token in `~/.git-credentials`:

    $ git config --global credential.helper store

After you log in during a `git push` with your username and token, the username or email address and token will be stored in the above location.

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

This function stages files that have been modified and deleted but new files that you have not added are not affected:

    $ git commit -a

This function commits any staged changes:

    $ git commit -m "message"

These arguments can be stacked as follows:

    $ git commit -am "Add your commit message here"

Note: Without `add`, `commit` will handle any changes to files that have been modified or deleted, but will not incorporate any files that have been created.

Then finally pushed:

    $ git push

If, for some reason, you would like to reset a commit:

    $ git reset

These commands can be chained together with the AND operator:

    $ git add . && git commit -am "Add your commit message here" && git push

## Stashing changes

If you forget to update a repository before making changes, you can "stash" those changes and then re-apply them after running `git pull`.

First, stash the changes:

    $ git stash

Then, update the local record of the repository:

    $ git pull

Finally, re-apply the changes you previously made:

    $ git stash apply

This has proven to be very useful for me when I forget to update a repository before making edits to the code.

## References

1. https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
2. https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup#_first_time
3. https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config
4. https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage#_credential_caching
5. https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning
6. https://www.geeksforgeeks.org/difference-between-chaining-operators-in-linux/