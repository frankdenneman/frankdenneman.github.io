---
title: "VMware tools disk timeout value Linux GOS"
date: 2010-04-28
categories: 
  - "vmware"
tags: 
  - "disk-timeout"
  - "linux"
  - "vmware"
  - "vmware-tools"
---

After I posted the ["VMtools increases TimeOutValue article"](http://frankdenneman.nl/2010/03/vcdx-tip-vmtools-increases-timeoutvalue/) I received a lot of questions if the VMware Tools automatically adjust the timeout value for Linux machines as well. Well, VMware Tools of versions ESX 3.5 Update 5 and ESX 4.0 install a udev rule file on Linux operating systems with kernel version equal or greater then 2.6.13. This rule file changes the default timeout value of VMware virtual disks to 180 seconds. This helps the guest operating system to better survive a SAN failure and keep the linux system disk from becoming read only. Because of the requirement of updates related to udev featured in the 2.6.13 kernel, the SCSI timeout value in other Linux kernels is not touched by the installation of VMware tools and the default value remains active. The two major Linux Kernel version each have a different timeout value: Linux 2.4 - 60 seconds Linux 2.6 - 30 seconds You can set the timeout value manually listed in /sys/block/_disk_/device/timeout. The problem is the distinction VMtools make between certain Linux Kernels, if you do not know this caveat you might end up with an Linux environment which is not configured exactly the same. This can lead to different behaviour during a SAN outage. Standardization is key when managing virtual infrastructure environments and a uniform environment eases troubleshooting A while ago Jason wrote an [excellent article](http://www.boche.net/blog/index.php/2009/10/29/vmware-esx-guest-os-io-timeout-settings-for-netapp-storage-systems/) about the values and benefit of increasing the guest os timeout
