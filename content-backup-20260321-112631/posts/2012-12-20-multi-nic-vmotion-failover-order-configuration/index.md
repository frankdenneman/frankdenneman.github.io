---
title: "Multi-NIC vMotion – failover order configuration"
date: 2012-12-20
categories: 
  - "vmotion"
---

After posting the article “[designing your vMotion network](http://frankdenneman.nl/2012/12/18/designing-your-vmotion-network/ "Designing your vMotion network")” I quickly received the question which failover order configuration is better. Is it better to configure the redundant NIC(s) as standby or as unused? The short answer: always use standby and never unused! Tomas Fojta posted the comment that it does not make sense to place the NICs into standby mode:

> In the scenario as depicted in the diagram I prefer to use active/unused. If you think about it the standby option does not give you anything as when one of the NICs fails both vmknics will be on the same NIC which does not give you anything.

Although it does not provide any performance benefits having vMotion routing the traffic across the same physical NIC during a NIC failure, there are two important reasons for providing redundant connection to each vmknic:

1. Abstraction layer
2. Using a default interface for management traffic

**Abstraction layer** As mentioned in the previous article, vMotion operations are done at the vmknic level. Due to vMotion focussing on the vmknic layer instead of the physical layer, some details are abstracted from vMotion load balancing logic such as the physical NIC’s link state or health. Due to this abstraction vMotion just selects the appopriate vmknics for load balancing network packets and trusts that there is connectivity between the vmknics of the source and destination host. [![](images/00-multi-nic-layers.png "00-multi-nic layers")](http://frankdenneman.nl/wp-content/uploads/2012/12/00-multi-nic-layers.png) **Default interface** Although vMotion is able to use multiple vmknics to load balance traffic, vMotion assigns one vmknic as its default interface and prefers to use this for connection management and some trivial management transmissions. \* As such, if you've got multiple physical NICs on a host that you plan to use for vMotion traffic, it makes sense to mark them as standby NICs for the other vMotion vmknics on the host. That way, even if you lose a physical NIC, you won't see vMotion network connectivity issues. This means that if you have designated three physical NICs for vMotion your vmknic configuration should look as follows:

| **VMknic** | **Active NIC** | **Standby NIC** |
| --- | --- | --- |
| vmknic0 | NIC1 | NIC2, NIC3 |
| vmknic1 | NIC2 | NIC1, NIC3 |
| vmknic2 | NIC3 | NIC1, NIC2 |

By placing the redundant NICs into standby instead of unused you avoid the risk of having an unstable vMotion network. If a NIC fails, you might experience some vMotion performance degradation as the traffic gets routed through the same NIC, but you can trust your vMotion network to correclty migrate all virtual machines off the host in order for to replace the faulty NIC. **\* Word to the wise** By writing about the fact that vMotion designates a vmknic to be the default interface I’m aware that this triggers and sparks the interest of some of the creative minds in our community. Please do not attempt to figure out which vmknic is designated as default interface and make that specific vmknic redundant and different from the rest. To paraphrase Albert Einstein: “Simplicity is the root of all genius”. Keep your Multi-NIC consistent and identical within the host and throughout all hosts. This saves you a lot of frustration during troubleshooting. Being able to depend on your vMotion network to migrate the virtual machines safely and correctly is worth its weight in gold. [Part 1 - Designing your vMotion network](http://frankdenneman.nl/2012/12/18/designing-your-vmotion-network/ "Part 1 - Designing your vMotion network") [Part 3 – Multi-NIC vMotion and NetIOC](http://frankdenneman.nl/2013/01/18/designing-your-vmotion-network-multi-nic-and-netioc/ "Designing your vMotion network – Multi-NIC vMotion and NetIOC") [Part 4 – Choose link aggregation over Multi-NIC vMotion?](http://frankdenneman.nl/2013/01/25/designing-your-vmotion-networking-choose-link-aggregation-over-multi-nic-vmotion/ "Designing your vMotion network – Choose link aggregation over Multi-NIC vMotion?") [Part 5 – 3 reasons why I use a distributed switch for vMotion networks](http://frankdenneman.nl/2013/01/30/designing-your-vmotion-network-3-reasons-why-i-use-a-distributed-switch-for-vmotion-networks/ "Designing your vMotion network – 3 reasons why I use a distributed switch for vMotion networks")
