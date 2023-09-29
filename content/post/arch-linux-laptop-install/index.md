---
title: Arch Linux Laptop Install
description: Guide to Arch Linux install on Lenovo ThinkPad E15 Gen 2.
# slug: hello-world
date: 2023-09-29 00:00:01+0000
# image: cover.jpg
categories:
    - Tech
tags:
    - Arch Linux
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

This is the basic framework that I use to install Arch Linux, with a few changes catered to the Lenovo ThinkPad E15 Gen 2. I have found that this is a decent mid range laptop, excellent linux compatibility, great keyboard, and overall provides a good value.

# Getting Started

This tutorial assumes the following:

* You are booting from a USB drive with the Arch install ISO
* Wireless or wired network is detected and drivers are configured automatically
* You want drive encrytion on your root partition, but not on your boot/efi/swap partitions

## Configure Wireless

```html
The following command will drop you into the iwd daemon:
# iwctl

From there:
# device list
# station *device* scan
# station *device* get-networks
# station *device* connect *SSID*
```

## Verify UEFI boot mode: 

> # ls /sys/firmware/efi/efivars 
> Note: The above command should show directory without error

## Verify internet connectivity: 

> # ping archlinux.org 

## Update system clock: 

> # timedatectl set-ntp true 
> # timedatectl status 



The following HTML `<h1>`—`<h6>` elements represent six levels of section headings. `<h1>` is the highest section level while `<h6>` is the lowest.

# H1
## H2
### H3
#### H4
##### H5
###### H6

## Paragraph

Xerum, quo qui aut unt expliquam qui dolut labo. Aque venitatiusda cum, voluptionse latur sitiae dolessi aut parist aut dollo enim qui voluptate ma dolestendit peritin re plis aut quas inctum laceat est volestemque commosa as cus endigna tectur, offic to cor sequas etum rerum idem sintibus eiur? Quianimin porecus evelectur, cum que nis nust voloribus ratem aut omnimi, sitatur? Quiatem. Nam, omnis sum am facea corem alique molestrunt et eos evelece arcillit ut aut eos eos nus, sin conecerem erum fuga. Ri oditatquam, ad quibus unda veliamenimin cusam et facea ipsamus es exerum sitate dolores editium rerore eost, temped molorro ratiae volorro te reribus dolorer sperchicium faceata tiustia prat.

Itatur? Quiatae cullecum rem ent aut odis in re eossequodi nonsequ idebis ne sapicia is sinveli squiatum, core et que aut hariosam ex eat.

## Blockquotes

The blockquote element represents content that is quoted from another source, optionally with a citation which must be within a `footer` or `cite` element, and optionally with in-line changes such as annotations and abbreviations.

### Blockquote without attribution

> Tiam, ad mint andaepu dandae nostion secatur sequo quae.
> **Note** that you can use *Markdown syntax* within a blockquote.

### Blockquote with attribution

> Don't communicate by sharing memory, share memory by communicating.<br>
> — <cite>Rob Pike[^1]</cite>

Welcome to Hugo theme Stack. This is your first post. Edit or delete it, then start writing!

For more information about this theme, check the documentation: https://stack.jimmycai.com/

Want a site like this? Check out [hugo-theme-stack-stater](https://github.com/CaiJimmy/hugo-theme-stack-starter)

> Photo by [Pawel Czerwinski](https://unsplash.com/@pawel_czerwinski) on [Unsplash](https://unsplash.com/)