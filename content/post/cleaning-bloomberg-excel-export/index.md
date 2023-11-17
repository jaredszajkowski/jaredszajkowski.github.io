---
title: Cleaning A Bloomberg Data Excel Export
description: A python function to clean and format an excel data export from Bloomberg.
# slug: hello-world
date: 2023-11-15 00:00:01+0000
lastmod: 2023-11-07 00:00:00+0000
# image: cover.jpg
draft: false
categories:
    - Financial Data
    - Tutorials
tags:
    - Python
    - Bloomberg
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

In this tutorial, we will write a python function that imports an excel export from Bloomberg, removes ancillary rows and columns, and leaves the data in a format where it can then be used in time series analysis.

## Example of a Bloomberg excel export

We will use the SPX index data in this example. Exporting the data from Bloomberg using the excel Bloomberg add-on yields data in the following format:

![Format of data in excel export from Bloomberg](Format_of_data_in_excel_export_from_Bloomberg.png)

## Data modifications

The above format isn't horrible, but we want to perform the following modifications:

1. Remove the first six rows of the data
2. Convert the 7th row to become column headings
3. Rename column 2 to "Close" to represent the closing price
4. Remove column 3, as we are not concerned about volume
5. Make the name of the excel worksheet "data"

## Assumptions

The remainder of this tutorial assumes that your excel file is named "SPX_Index.xlsx", and the worksheet is named "Worksheet".

## Python function to modify the data

The following function will perform the modifications mentioned above:

```html
import pandas as pd

# This function takes an excel export from Bloomberg and 
# removes all excess data leaving date and close columns

def bb_data_updater(fund):
    # File name
    file = fund + "_Index.xlsx"
    
    # Import data from file as dataframe and drop rows and columns
    data = pd.read_excel(file, sheet_name = 'Worksheet', engine='openpyxl')
    data.columns = data.iloc[5]
    data.rename_axis(None, axis=1, inplace = True)
    data.drop(data.index[0:6], inplace=True)
    data.set_index('Date', inplace = True)
    
    try:
        data.drop(columns = {'PX_VOLUME'}, inplace = True)
    except KeyError:
        pass
        
    data.rename(columns = {'PX_LAST':'Close'}, inplace = True)
    data.sort_values(by=['Date'], inplace = True)
    
    # Export data to excel
    file = fund + ".xlsx"
    data.to_excel(file, sheet_name='data')
    
    # Output confirmation
    print(f"The last date of data for {fund} is: ")
    print(data[-1:])
    print(f"Bloomberg data conversion complete for {fund} data")
    return print(f"--------------------")
```

Let's break this down line by line.

## Imports

First, we need to import pandas:

    import pandas as pd

## 




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