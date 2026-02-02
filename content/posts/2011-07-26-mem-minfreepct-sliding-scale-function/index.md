---
title: "Mem.MinFreePct sliding scale function"
date: 2011-07-26
categories: 
  - "memory"
tags: 
  - "vsphere-5"
---

One of the cool “under the hood” improvements vSphere 5 offers is the sliding scale function of the Mem.MinFreePct. Before diving into the sliding scale function, let’s take a look at the Mem.MinFreePct function itself. MinFreePct determines the amount of memory the VMkernel should keep free. This threshold is subdivided in various memory thresholds, i.e. High, Soft, Hard and Low and is introduced to prevent performance and correctness issues. The threshold for the low state is required for correctness. In other words, it protects the VMkernel layer from PSOD’s resulting from memory starvation. The soft and hard thresholds are about virtual machine performance and memory starvation prevention. The VMkernel will trigger more drastic memory reclamation techniques when it approaches the Low state. If the amount of free memory is just a bit less than the Min.FreePct threshold, the VMkernel applies ballooning to reclaim memory. The ballooning memory reclamation technique introduces the least amount of performance impact on the virtual machine by working together with the Guest operating system inside the virtual machine, however there is some latency involved with ballooning. Memory compressing helps to avoid hitting the low state without impacting virtual machine performance, but if memory demand is higher than the VMkernels’ ability to reclaim, drastic measures are taken to avoid memory exhaustion and that is swapping. However swapping will introduce VM performance degradations and for this reason this reclamation technique is used when desperate moments require drastic measurements. For more information about reclamation techniques I recommend reading the “[disable ballooning](http://frankdenneman.nl/2010/11/disable-ballooning/)” article. vSphere 4.1 allowed the user to change the default MinFreePct value of 6% to a different value and introduced a dynamic threshold of the Soft, Hard and Low state to set appropriate thresholds and prevent virtual machine performance issues while protecting VMkernel correctness. By default vSphere 4.1 thresholds was set to the following values:

| **Free memory state** | **Threshold** | **Reclamation mechanism** |
| --- | --- | --- |
| High | 6% | None |
| Soft | 64% of MinFreePct | Balloon, compress |
| Hard | 32% of MinFreePct | Balloon, compress, swap |
| Low | 16% of MinFreePct | Swap |

Using a default MinFreePct value of 6% can be inefficient in times where 256GB or 512GB systems are becoming more and more mainstream. A 6% threshold on a 512GB will result in 30GB idling most of the time. However not all customers use large systems and prefer to scale out than to scale up. In this scenario, a 6% MinFreePCT might be suitable. To have best of both worlds, ESXi 5 uses a sliding scale for determining its MinFreePct threshold.

| **Free memory state threshold** | **Range** |
| --- | --- |
| 6% | 0-4GB |
| 4% | 4-12GB |
| 2% | 12-28GB |
| 1% | Remaining memory |

Let’s use an example to explore the savings of the sliding scale technique. On a server configured with 96GB RAM, the MinFreePct threshold will be set at 1597.6MB, opposed to 5898.24MB if 6% was used for the complete range 96GB.

| **Free memory state** | **Threshold** | **Range** | **Result** |
| --- | --- | --- | --- |
| High | 6% | 0-4GB | 245.96MB |
|  | 4% | 4-12GB | 327.68MB |
|  | 2% | 12-28GB | 327.68MB |
|  | 1% | Remaining memory | 696.32MB |
| **Total High Threshold** |  |  | **1597.60MB** |

Due to the sliding scale, the MinFreePct threshold will be set at 1597.96MB, resulting in the following Soft, Hard and low threshold:

| **Free memory state** | **Threshold** | **Reclamation mechanism** | **Threshold in MB** |
| --- | --- | --- | --- |
| Soft | 64% of MinFreePct | Balloon | 1022.69 |
| Hard | 32% of MinFreePct | Balloon, compress | 511.23 |
| Low | 16% of MinFreePct | Balloon, compress, swap | 255.62 |

Although this optimization isn’t as sexy as Storage DRS or one of the other new features introduced by vSphere5 it is a feature of vSphere 5 that helps you drive your environments to higher consolidation ratios.
