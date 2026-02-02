---
title: "Adjusting the cost of vMotion – a word of caution"
date: 2013-01-15
categories: 
  - "drs"
  - "vmotion"
  - "vmware"
---

Yesterday I posted an article on [how to change the cost of vMotion](http://frankdenneman.nl/2013/01/14/limiting-the-number-of-concurrent-vmotions/ "Limiting the number of concurrent vMotions") in order to change the default number of concurrent vMotion. As I mentioned in the article, I’m not a proponent of changing advanced settings.

Today Kris posted a very interesting question;

> How about the scenario where one uses multi NIC vMotion for against two 5Gbps virtual adapters)? I know a cost of 4 will be set for the network by the VMkernel, however as the aggregate bandwidth becomes 10Gbps is it safe enough to raise the limit? Perhaps not to the full 8 for 10Gbps, but 6?

[![vMotion system resource pool](images/vMotion-system-resource-pool.png)](http://frankdenneman.nl/wp-content/uploads/2012/12/vMotion-system-resource-pool.png)

Please note that this article does not bash Kris. He provides a use case that I’ve heard a couple of times, making his comment an example use case. Although Kris’s scenario sounds like a very good use case to adjust the cost settings to circumvent the line-speed detection of the VMkernel to determine the max-cost of the network resource, it does not solve the other dynamic elements using line speed.

**DRS MaxMovesPerHost**  
ESX 4.1 Introduces the MaxMovesPerHost setting, allowing the host to dynamically set the limit on moves. The limit is based on how many moves DRS thinks can be completed in one DRS evaluation interval. DRS adapts to the frequency it is invoked (pollPeriodSec, default 300 seconds) and the average migration time observed from previous migrations. However, this limit is still bound by the detected line speed and the associated Max cost. Although the proposed environment has 10GB line speed in total available, the VMkernel will still set the max cost to allow 4 vMotions on the host. Restricting the number of migrations, DRS can initiate during a load balance operation.  

**vMotion system resource pool CPU reservation**  
vMotion tries to move the used memory blocks as fast as possible. vMotion uses all the available bandwidth depending on the available CPU speed and bandwidth. Depending on the detected line speed, vMotion reserves an X amount of CPU speed at the start of a vMotion process. vMotion computes its desired host vMotion CPU reservation. For every 1GBe vMotion link speed it detects vMotion in vSphere 5.1 reserved 10% of a CPU core with a minimum desired CPU reservation of 30%. This means that if you use a single 1GBe, vMotion reserves 30% of a core, if you use 4 x 1GBe connections, that means vMotion reserves 40% of a core. A 10GBe link is special as vMotion reserves 100% of a single core.  

vMotion creates a (system) resource pool and sets the appropriate CPU reservation on the resource pool. It’s important to note that this is being done to the vMotion resource pool, which means that the reservation is shared across all vMotions happening on the host.  
  
Using two 5GB links, results in a 40% CPU core reservation (default 30% plus 10% for the extra link). However, this dynamic behavior might get unnoticed if you have enough spare CPU cycles in your source and destination host.  

Word of caution  
I hope these two examples show that there are multiple dynamic elements working together on various levels in your virtual infrastructure. Adjusting a setting might improve the performance of a specific use case, but to change the overall behavior, lots of settings have to be changed. Due to the lack of time and specific information correlating various settings is impossible for many of us most of the time. Therefore I would like to repeat my recommendation. Please do not adjust advanced settings only if VMware supports ask you to.
