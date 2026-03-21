---
title: "Identify storage performance issues"
date: 2010-03-25
categories: 
  - "storage"
tags: 
  - "davgcmd"
  - "esxtop"
  - "vmware"
---

VMware has recently updated the kb article " [Using esxtop to identify storage performance issues Details](http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=1008205)" (KB1008205). The KB article provides information about how to use esxtop to determine the latency statistics across various devices. The article contain easy to follow, step-by-step instructions on how to setup ESXtop to monitor storage performance per HBA, LUN and virtual machine. It also list generic acceptable values to put your measured values in perspective. It's a great article, bookmark it for future reference. If you want to learn about threshold of certain metrics in ESXtop, please check out the [ESXtop metric bible](http://www.yellow-bricks.com/esxtop/) featured on Yellow-bricks.com. ESXtop is a great tool to view and measure certain criteria in real time, but sometimes you want to collect metrics for later reference. If this is the case, the tool vscsiStats might be helpful. vscsiStats is a tool to profile your storage environment and collects info such as outstanding IO, seekdistance and many many more. Check out Duncan's [excellent article](http://www.yellow-bricks.com/2009/12/17/vscsistats/) on how to use vscsiStats. Because vscsiStats will collect data in a .csv file you can create diagrams, Gabe written an [article](http://www.gabesvirtualworld.com/?p=1022) how to convert the vscsiStats data into excel charts.
