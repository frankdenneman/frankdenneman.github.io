---
title: "VCDX tip: VMtools increases TimeOutValue"
date: 2010-03-16
categories: 
  - "vcdx"
tags: 
  - "timeoutvalue"
  - "vcdx"
---

This is just a small heads-up post for all the VCDX candidates. Almost every VCDX application I read mentions the fact that they needed to increase the Disk TimeOutValue (HKEY\_LOCAL\_MACHINE/System/CurrentControlSet/Services/Disk) by to 60 seconds on Windows machines. The truth is that the VMware Tools installation (ESX version 3.0.2 and up) will change this registry value automatically. You might want to check your operational procedures documentation and update this! [VMware KB 1014](http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=1014)
