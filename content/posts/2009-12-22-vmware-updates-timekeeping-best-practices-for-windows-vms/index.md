---
title: "VMware updates Timekeeping best practices"
date: 2009-12-22
categories: 
  - "vmware"
tags: 
  - "time-synchronization"
---

A couple of weeks ago I [discovered](http://frankdenneman.wordpress.com/2009/09/18/timekeeping-best-practices-for-linux/) that VMware updated its timekeeping best practices for Linux virtual machines. December 7th VMware published a new best practice of timekeeping in Windows VMs. [(KB1318)](http://kb.vmware.com/kb/1318) VMware now recommends to use either W32Time or NTP for all virtual machines. This a welcome statement from VMware ending the age old question while designing a Virtual Infrastructure; Do we use VMware tools time sync or do we use W32time? If we use VMware tools, how do we configure the Active Directory controller VMs? VMware Tools can still be used and still function well enough for most non time sensitive application. VMware tools time sync is excellent in accelerating and catching up time if the time that is visible to virtual machines (called apparent time) is going slowly, but W32time and NTP can do one thing that VMware tools time sync can’t, that’s slowing down time. Page 15 of the (older) white paper: Timekeeping in VMware Virtual Machines [http://www.vmware.com/pdf/vmware\_timekeeping.pdf](http://www.vmware.com/pdf/vmware_timekeeping.pdf) explains the issue.

> However, at this writing, VMware Tools clock synchronization has a serious limitation: it cannot correct the guest clock if it gets ahead of real time (except in the case of NetWare guest operating systems).

For more info about timekeeping best practices for Windows VMs, please check out KB article 1318 [http://kb.vmware.com/kb/1318](http://kb.vmware.com/kb/1318) It appears that VMware updated the Timekeeping best practices for Linux guests as well. [http://kb.vmware.com/kb/1006427](http://kb.vmware.com/kb/1006427) (9 december 2009)
