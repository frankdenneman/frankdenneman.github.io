---
title: "Memory reclamation, when and how?"
date: 2010-06-11
categories: 
  - "memory"
tags: 
  - "ballooning"
  - "vmware"
---

After discussing with Duncan the performance problem presented by @heiner\_hardt , we discussed the exact moment the VMkernel decides which reclamation technique it will use and specific behaviors of the reclamation techniques. This article supplements Duncan's [article](http://www.yellow-bricks.com/2010/06/10/is-this-vm-actively-swapping-helping-heiner_hardt/) on Yellow-bricks.com. Now let's begin with when the kernel decides to reclaim memory and see how the kernel reclaims memory. So host physical memory is reclaimed based on four "free memory states", each with a corresponding threshold. Based on the Threshold, the VMkernel chooses which reclamation technique it will use to reclaim memory from virtual machines.

| **Free Memory state** | **Threshold** | **Reclamation technique** |
| --- | --- | --- |
| High | 6% | None |
| Soft | 4% | Ballooning |
| Hard | 2% | Ballooning and Swapping |
| Low | 1% | Swapping |

The high memory state has a threshold hold of 6%, that means that 6% of the ESX host physical memory minus the service console memory must be free. When the virtual machines use less than 94% of the host physical memory, the VMkernel will not reclaim memory because there is no need to, but when the memory usage starts to fall towards the free memory threshold the VMkernel will try to balloon memory. The VMkernel selects the virtual machines with the largest amounts of idle memory (detected by the idle memory tax process) and will ask the virtual machine to select it's idle memory pages. Now to do this the guest os needs to swap those pages, so if the guest is not configured with sufficient swap space, ballooning can become problematic. Linux behaves pretty worse in this situation, invoking OOM (out-of memory) killer when its swap space is full and starts to randomly kill processes. Back to the VMkernel, in the High and Soft state, ballooning if favored over swapping. If it ESX server cannot reclaim memory by ballooning in time before it reaches the Hard state, the ESX turns to swapping. Swapping has proven to be a sure thing within a limited amount of time. Opposite of the balloon driver, which tries to understand the needs of the virtual machine let the guest decides whether and what to swap, the swap mechanism just brutally picks pages at random from the virtual machine, this impacts the performance of the virtual machine but will help the VMkernel to survive. Now the fun thing is, before the VMkernel detects the free memory is reaching the soft threshold, it will start to request pages through the balloon driver (vmmemctl), this is because it takes time for the Guest OS to respond to the vmmemctl driver with suitable pages. By starting prematurely, the VMkernel tries to avoid the situation that it will reach the Soft state or worse. So you can see ballooning occurring sometimes before the Soft state is reached. (between 6 and 4% free memory) One exception is the virtual machine memory limit, if a limit is set on the virtual machine, the VMkernel always tries to balloon or swap pages of the virtual machine after reaching its limit, even if the ESX host has enough free memory available.
