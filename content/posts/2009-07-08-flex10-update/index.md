---
title: "Flex10 update"
date: 2009-07-08
categories: 
  - "networking"
tags: 
  - "flex10"
  - "nc373i"
  - "virtual-connect"
---

In my first post I had a question about the path data travels when sent to a “standby” virtual connect module. To quote my own question :

> “What will happen if the VMkernel decides to use that nic to send IO? Is the Flexnic aware of the standby status of it “native” uplink? Will it send data to the uplink of the VC module it’s connected to or will it send data to the active uplink? How is this done? Will it send the IO through the midplane or CX-4 cable to the VC module with the active uplink? And if this occurs what will be the added latency of this behavior? HP describes the standby status as blocked, what does this mean? Will virtual connect discard IO send to the standby IO, will it not accept IO and how will it indicate this?” <!--more-->

The virtualconnect module is not standby, it’s external( X1 thru x6) ports are standby. The blade can and will send I/O to the virtualconnect module. It is the only way, because the blade NIC is hardwired to that VC module. When the virtual connect module receives data, it will transfer the data to the Virtual Connect module with the active ports over its internal X0 port. The X0 port is also mentioned in the HP documentation as cross connect. HP beefed up the cross connects in theThe Flex10 module, it has 2 x 10 cross connects instead of the 1 x 10 cross connect found in the 1/10 virtual connect module BL460c G1 NC373i 1GB Nics bandwidth upgrade The new BL460cG6 blade has a Flex10 LOM adapter, when using G6 blades along G1 blades in a C7000 enclosure It might be nice to swap the 1/10 virtual connect module for Flex10 virtual connect modules. When a NC373i is connected to a flex10 VC module the link speed of the 1GB module will be upgraded to 2,5 GB. It does not automatically upgrade the bandwidth when installing the Flex10 module, a firmware upgrade of the NC373i nic is needed. Download the network firmware update tool from the HP support site (date 7 oct 2008, version 2.1.3.1). The updated version of the boot code, 4.4.1 that enables the 2.5 Gigabit support. Windows 2003 will not show the proper uplink speed. I haven’t checked it on a windows 2008 server. But to be certain Check the Flex10 virtual connect module to see which speed the nic is linked to.
