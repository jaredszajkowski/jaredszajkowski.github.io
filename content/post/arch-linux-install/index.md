---
title: Arch Linux Install
description: Guide to Arch Linux install with customizations for the  Lenovo ThinkPad E15 Gen 2.
# slug: hello-world
date: 2023-09-29 00:00:01+0000
lastmod: 2023-11-07 00:00:00+0000
# image: cover.jpg
draft: false
categories:
    - Tech
    - Tutorials
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

### Verify UEFI boot mode

The following command should show directory without error:

    # ls /sys/firmware/efi/efivars

### Configure wireless network

The following command will drop you into the iwd daemon:

    # iwctl

From there:

    # device list
    # station *device* scan
    # station *device* get-networks
    # station *device* connect *SSID*

### Verify internet connectivity

    # ping archlinux.org

### Update system clock

    # timedatectl set-ntp true
    # timedatectl status

## Disks, partition table & partitions

The following assumes that your NVME drive is found as /dev/nvme0n1. Partitions will then be /dev/nvme0n1p1 and so on.

### Wipe disk

List disks:

    # fdisk -l

Wipe all file system records:

    # wipefs -a /dev/nvme0n1

### Create new partition table

Open nvme0n1 with gdisk:

    # gdisk /dev/nvme0n1

Create GPT partition table with option "o".

### Create EFI partition

Create new EFI partition w/ 550mb with option "n", using the following parameters:

    Partition #1
    Default starting sector
    +550M
    Change partition type to EFI System (ef00)

### Create boot partition

Create new boot partition w/ 550mb with option "n", using the following parameters:

    Partition #2
    Default starting sector
    +550M
    Leave default type of 8300

### Create swap partition

The old rule of thumb used to be that a swap partition should be the same size as the amount of memory in the system, but given the typical amount of memory in modern systems this is obviously no longer necessary. For my system with 16 or 32 GB of memory, a swap of 8 GB is rarely even used.</br>

Create new Swap partition w/ 8GB with option "n", using the following parameters:

    Partition #3
    Default starting sector
    +8G
    Change to linux swap (8200)

### Create root partition

Create new root partition w/ remaining disk space with option "n", using the following parameters:

    Partition #4
    Default starting sector
    Remaining space
    Linux LUKS type 8309

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

## System install

### Install base packages

    # pacstrap /mnt base base-devel linux linux-firmware grub-efi-x86_64 efibootmgr

### Generate fstab

    # genfstab -U /mnt >> /mnt/etc/fstab

### Enter new system

    # arch-chroot /mnt /bin/bash

### Set clock

    # ln -sf /usr/share/zoneinfo/America/Chicago /etc/localtime
    # hwclock –systohc

### Generate locale

In /etc/locale.gen **uncomment only**: en_US.UTF-8 UTF-8

    # locale-gen

In /etc/locale.conf, you should **only** have this line: LANG=en_US.UTF-8

    # nano /etc/locale.conf

### Set hostname & update hosts

    # echo linuxmachine > /etc/hostname

Update /etc/hosts with the following:

    127.0.0.1   localhost
    ::1         localhost
    127.0.1.1   linuxmachine.localdomain    linuxmachine

### Set root password

    # passwd

### Update /etc/mkinitcpio.conf & generate initrd image

Edit /etc/mkinitcpio.conf with the following:

    HOOKS=(base udev autodetect modconf block keymap encrypt resume filesystems keyboard fsck)

Then run:

    # mkinitcpio -p linux

### Install grub

    # grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=ArchLinux

Edit /etc/default/grub so it includes a statement like this:

    GRUB_CMDLINE_LINUX="cryptdevice=/dev/nvme0n1p4:archcryptroot resume=/dev/nvme0n1p3"

Generate final grub configuration:

    # grub-mkconfig -o /boot/grub/grub.cfg

### Exit & reboot

    # exit
    # umount -R /mnt
    # swapoff -a
    # reboot

To be continued.
