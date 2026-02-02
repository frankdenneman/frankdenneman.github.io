---
title: "Impact of oversized virtual machines part 1"
date: 2010-12-16
categories: 
  - "vmware"
---

Recently we had an internal discussion about the overhead an oversized virtual machine generates on the virtual infrastructure. An oversized virtual machine is a virtual machine that consistently uses less capacity than its configured capacity. Many organizations follow vendor recommendations and/or provision virtual machine sized according to the wishes of the customer i.e. more resources equals better performance. By oversizing the virtual machine you can introduce the following overhead or even worse decrease the performance of the virtual machine or other virtual machines inside the cluster. **Note**: This article does not focus on large virtual machines that are correctly configured for their workloads. **Memory overhead** Every virtual machine running on an ESX host consumes some memory overhead additional to the current usage of its configured memory. This extra space is needed by ESX for the internal VMkernel data structures like virtual machine frame buffer and mapping table for memory translation, i.e. mapping physical virtual machine memory to machine memory. The VMkernel will calculate a static overhead of the virtual machine based on the amount of vCPUs and the amount of configured memory. Static overhead is the minimum overhead that is required for the virtual machine startup. DRS and the VMkernel uses this metric for Admission Control and vMotion calculations. If the ESX host is unable to provide the unreserved resources for the memory overhead, the VM will not be powered on, in case of vMotion, if the destination ESX host must be able to back the virtual machine reservation and the static overhead otherwise the vMotion will fail. The following table displays a list of common static memory overhead encountered in vSphere 4.1. For example, a 4vCPU, 8GB virtual machine will be assigned a memory overhead reservation of 413.91 MB regardless if it will use its configured resources or not.

| Memory (MB) | 2vCPUs | 4vCPUs | 8vCPUs |
| --- | --- | --- | --- |
| 2048 | 198.20 | 280.53 | 484.18 |
| 4096 | 242.51 | 324.99 | 561.52 |
| 8192 | 331.12 | 413.91 | 716.19 |
| 16384 | 508.34 | 591.76 | 1028.07 |

The VMkernel treats virtual machine overhead reservation the same as VM-level memory reservation and it will not reclaim this memory once it has been used, furthermore memory overhead reservations will not be shared by transparent page sharing. **Shares (size does not translate into priority)** By default each virtual machine will be assigned a specific amount of shares. The amount of shares depends on the share level, low, normal or high and the amount of vCPUs and the amount of memory.

| Share Level | Low | Normal | High |
| --- | --- | --- | --- |
| Shares per CPU | 500 | 1000 | 2000 |
| Shares per MB | 5 | 10 | 20 |

I.e. a virtual machine configured with 4CPUs and 8GB of memory with normal share level receives 4000 CPU shares and 81960 memory shares. Due to relating amount of shares to the amount of configured resources this “algorithm” indirectly implies that a larger virtual machine needs to receive a higher priority during resource contention. This is not true, as some business critical applications perfectly are run on virtual machines configured with low amounts of resources. **Oversized VMs on NUMA architecture** vSphere 4.1 CPU scheduler has undergone optimization to handle virtual machines which contains more vCPUs than available cores on one NUMA physical CPU. The virtual machine (wide-vm) will be spread across the minimum number of NUMA nodes, but memory locality will be reduced, as memory will be distributed among its home NUMA nodes. This means that a vCPU running on one NUMA node might needs to fetch memory from its other NUMA node. Leading to unnecessary latency, CPU wait states, which can lead to %ready time for other virtual machines in high consolidated environments. Wide-NUMA nodes are of great use when the virtual machine actually run load comparable to its configured size, it reduces overhead compared to the 3.5/4.0 CPU scheduler, but it still will be better to try to size the virtual machine equal or less than the available cores in a NUMA node. More information about CPU scheduling and NUMA architectures can be found here: [http://frankdenneman.nl/2010/09/esx-4-1-numa-scheduling/](http://frankdenneman.nl/2010/09/esx-4-1-numa-scheduling/) Go to [Part 2: Impact of oversized virtual machine on HA and DRS](http://frankdenneman.nl/2010/12/impact-of-oversized-virtual-machines-part-2/)
