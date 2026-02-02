---
title: "Resource pools and avoiding HA slot sizing"
date: 2010-02-24
categories: 
  - "drs"
  - "memory"
tags: 
  - "ha-slot-size"
  - "memory-reservations"
  - "resource-pools"
---

Virtual machines configured with large amounts of memory (16GB+) are not uncommon these days. Most of the time these “heavy hitters” run mission critical applications so it’s not unusual setting memory reservations to guarantee the availability of memory resources. If such a virtual machine is placed in a HA cluster, these significant memory reservations can lead to a very conservative consolidation ratio, due to the impact on HA slot size calculation. (For more information about slot size calculation, please review the [HA deep dive](http://www.yellow-bricks.com/vmware-high-availability-deepdiv/) page on yellow-bricks.com.) There are options to avoid creation of large slot sizes. Such as not setting reservations, disabling strict admission control, using vSphere new admission control policy “percentage of cluster resources reserved” or creating a custom slot size by altering the advanced settings das.vmMemoryMinMB. But what if you are still using ESX 3.5, must guarantee memory resources for that specific VM, do not want to disable strict admission control or don’t like tinkering with the custom slot size setting? Maybe using the resource pool workaround can be an option. **Resource pool workaround** During a conversation with my colleague Craig Risinger, author of the very interesting article “[The resource pool priority pie paradox](http://www.yellow-bricks.com/2010/02/22/the-resource-pool-priority-pie-paradox/)”, we discussed the lack of relation between resource pools reservation settings and High Availability. As Craig so eloquently put it:

> “RP reservations will not muck around with HA slot sizes”

High Availability ignores resource pools reservation settings when calculating the slot size, so if a single VM is placed in a resource pools with memory reservation configured, it will have the same effect on resource allocation as per VM memory reservation, but does not affect the HA slot size. By creating a resource pool with a substantial memory setting you can avoid decreasing the consolidation ratio of the cluster and still guarantee the virtual machine its resources. Publishing this article does not automatically mean that I’m advocating using this workaround on a regular basis. I recommend implementing this workaround very sparingly as creating a RP for each VM creates a lot of administrative overhead and makes the host and cluster view a very unpleasant environment to work in. A possible scenario to use this workaround can be when implementing MS Exchange 2010 mailbox servers. These mailbox servers are notorious for demanding a huge amount of memory and listed by many organizations as mission critical servers. To emphasize it once more, this is not a best practice! But it might be useful in certain scenarios to avoid large slots and therefore low consolidation ratios.
