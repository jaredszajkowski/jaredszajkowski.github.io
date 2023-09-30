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

## Getting started

This tutorial assumes the following:

* You are booting from a USB drive with the Arch install ISO.
* Wireless or wired network is detected and drivers are configured automatically.
* You want drive encrytion on your root partition, but not on your boot/efi/swap partitions.

### Configure Wireless

The following command will drop you into the iwd daemon:

    # iwctl

From there:

    # device list
    # station *device* scan
    # station *device* get-networks
    # station *device* connect *SSID*

### Verify UEFI boot mode

The following command should show directory without error:

    # ls /sys/firmware/efi/efivars

### Verify internet connectivity

    # ping archlinux.org

### Update system clock

    # timedatectl set-ntp true
    # timedatectl status

## Prep disks

The following assumes that your NVME drive is found as /dev/nvme0n1. Partitions will then be /dev/nvme0n1p1 and so on.

List disks:

    # fdisk -l

Wipe all file system records:

    # wipefs -a /dev/nvme0n1

## Partition table & partitions

Open nvme0n1 with gdisk:

    # gdisk /dev/nvme0n1

Create GPT partition table with option "o".

### Create EFI partition

Create new EFI partition w/ 550mb with option "n", using the following parameters:

<font color="dark blue">
Partition #1 </br>
Default starting sector</br>
+550M</br>
Change partition type to EFI System (ef00)</br>
</font>

### Create boot partition

Create new boot partition w/ 550mb with option "n", using the following parameters:

<font color="dark blue">
Partition #2 </br>
Default starting sector</br>
+550M</br>
Leave default type of 8300</br>
</font>

### Create swap partition

The old rule of thumb used to be that a swap partition should be the same size as the amount of memory in the system, but given the typical amount of memory in modern systems this is obviously no longer necessary. For my system with 16 or 32 GB of memory, a swap of 8 GB is rarely even used.</br>

Create new Swap partition w/ 8GB with option "n", using the following parameters:

<font color="dark blue">
Partition #3</br>
Default starting sector</br>
+8G</br>
Change to linux swap (8200)</br>
</font>

### Create root partition

Create new root partition w/ remaining disk space with option "n", using the following parameters:

<font color="dark blue">
Partition #4</br>
Default starting sector</br>
Complete remaining space</br>
Linux LUKS type 8309</br>
</font>

And then exit gdisk.

## Write file systems

### EFI partition

Write file system to new EFI System partition:

    # cat /dev/zero > /dev/nvme0n1p1 
    # mkfs.fat -F32 /dev/nvme0n1p1 

### Boot partition

Then boot partition:

    # cat /dev/zero > /dev/nvme0n1p2 
    # mkfs.ext2 /dev/nvme0n1p2

### Root partition

Prepare root partition w/ LUKS:

    # cryptsetup -y -v luksFormat --type luks2 /dev/nvme0n1p4
    # cryptsetup luksDump /dev/nvme0n1p4
    # cryptsetup open /dev/nvme0n1p4 archcryptroot
    # mkfs.ext4 /dev/mapper/archcryptroot
    # mount /dev/mapper/archcryptroot /mnt

I use *archcryptroot* for the name of my encrypted volume, but change as necessary.

### Swap partition

Then swap:

    # mkswap /dev/nvme0n1p3
    # swapon /dev/nvme0n1p3

### Create mount points

    # mkdir /mnt/boot
    # mount /dev/nvme0n1p2 /mnt/boot
    # mkdir /mnt/boot/efi
    # mount /dev/nvme0n1p1 /mnt/boot/efi

## Install system

To be continued.