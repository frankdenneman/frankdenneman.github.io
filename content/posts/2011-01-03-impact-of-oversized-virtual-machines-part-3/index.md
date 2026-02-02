---
title: "Impact of oversized virtual machines part 3"
date: 2011-01-03
categories: 
  - "cpu"
  - "memory"
tags: 
  - "bootstorms"
  - "numa"
  - "vmware"
---

In [part 1](http://frankdenneman.nl/2010/12/impact-of-oversized-virtual-machines-part-1/) of the series of post on the impact of oversized virtual machines NUMA architecture, memory overhead reservation and share levels are reviewed, [part 2](http://frankdenneman.nl/2010/12/impact-of-oversized-virtual-machines-part-2/) zooms in on the impact of memory overhead reservation and share levels on HA and DRS. This part looks at CPU scheduling, memory management and what impact oversized virtual machines have on the environment when a bootstorm occurs. **Multiprocessor virtual machine** In most cases, adding more CPUs to a virtual machine does not automatically guarantee increase throughput of the application, because some workloads cannot always take advantage of all the available CPUs. Sharing resources and scheduling these processes will introduce additional overhead. For example, a four-way virtual machine is not four times as productive as a single-CPU system. If the application is unable to scale than the application will not benefit from these additional available resource.

**Progress** Although relaxed co-scheduling reduces the requirement of the VMkernel to simultaneous schedule all vCPUs of the virtual machine, periodically scheduling the unused or idle vCPUs is still necessary to keep the progress of each vCPU in the virtual machine acceptably synchronized.

Esxtop also gives scheduling stats for SMP virtual machines;

_%CRUN:_ All VCPUs want to run at once. CRUN is the amount of time between when a PCPU is told to run a certain VCPU on an SMP VM and when it is actually able to run that VM. This should be almost 0.

_%CSTOP_: If a VCPU gets ahead of another VCPU of the same SMP VM, then we ask the faster VCPU to stop until the other one can catch up. The time spent in this stopped state is CSTOP.

**Single thread application** Only applications with multiple threads and allow them to be scheduled in parallel can benefit from multiprocessor systems. A single-threaded application can only be scheduled on one CPU at the time and will not benefit from the multiple CPUs available. The Guest OS is able to migrate the thread between the available CPUs, introducing unnecessary overhead such as interrupts or context switches and cache misses.

**Timer interrupts** In older guest operating systems, the unused virtual CPUs still take timer interrupts, which consumes a small amount of additional CPU. Please refer to KB articles “[High CPU Utilization of Inactive Virtual Machines - KB1077](http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=1077)”

**Configured memory** Oversizing the memory configuration of a virtual machine can impact the performance of the virtual machine itself or even worse, impact the other active virtual machines on the host and in the cluster. Using memory reservations on oversized virtual machines will make it go from bad to worse.

**Application memory management** Excess memory is a problem when the application uses this memory opportunistically, in other words the application is hoarding memory. Java, SAP and often Oracle workloads assume it can use all the memory it detects. Because ESX cannot determine which memory is important to the virtual machine, it always backs memory pages of the virtual machine with physical pages. Besides creating a large memory footprint on the physical level, these kinds of applications add a third level of memory management as well.

Due to this additional management level, the Guest OS does not understand which pages are important and which are not. And because the Guest OS isn’t aware, it can not return inactive pages to the balloon driver when requested, therefor impacting the performance of the application during contention even more.

Setting memory reservation at virtual machine level will guarantee the availability of physical memory and will secure a certain level of application performance (if memory bound). However setting memory reservations at virtual machine level will impact the virtual infrastructure and the larger the memory reservation, the larger the impact. Visit “[Impact of memory reservation](http://frankdenneman.nl/2009/12/impact-of-memory-reservation/)” for more info.

To avoid these effects, it is recommended to monitor the behavior of the application over time and tune the configuration of the virtual machine and its reservation to get proper performance and limit the impact of its configured memory and the memory reservation.

**NUMA node** If the virtual machines mentioned in the previous paragraph are configured with more memory than available in their home NUMA node, the system needs to fetch the memory from remote NUMA nodes. Accessing memory from remote nodes introduces latencies and generally reduced throughput of the vCPU. ESX does not communicate any NUMA information to the Guest OS and therefore both the Guest OS as well as the application are unaware of the non-uniform latency characteristics of the underlying platform. The Guest OS and application are therefor unable to prioritize which memory it will use.

If the virtual machine uses all the available memory of a NUMA node, it will lead to a higher degree of remote memory of all the other active virtual machines using the pCPU, leading to higher memory latencies and less throughput of the other virtual machines and eventually an intra-node migration. For more information about NUMA nodes, please read the articles: [Sizing VMs and NUMA nodes](http://frankdenneman.nl/2009/12/impact-of-memory-reservation/) and [ESX 4.1 NUMA Scheduling](http://frankdenneman.nl/2010/09/esx-4-1-numa-scheduling/).

Attempt to configure virtual machine with less memory than available in a NUMA node.

**Swap file** During boot a swap file is created that equals the virtual machines configured memory minus the configured memory reservation. If no memory reservation is set, the virtual machine swap file (.vswap) equals the configured memory. Large virtual machines will generate an additional requirement for storing these large swap files reducing the consolidation ratio of virtual machines per VMFS datastore.

**Bootstorms**

> A bootstorm is the occurrence of powering on a multitude of virtual machines simultaneously.

Virtual infrastructures running versions prior to ESX 4.1 can encounter memory contention when a bootstorm occurs of virtual machines running windows. Windows checks how much memory is available to the OS by zeroing out pages it detects. Transparent page sharing will collapse these pages but this will not occur immediately. Transparent Page Sharing is a cycle-driven process that tries to make a pass over the virtual machine memory with a timeframe of 3600 seconds. The level of contention will impact the speed of the TPS process. During a bootstorm, this zero-out behavior and delayed TPS process can introduce contention. Usually this contention is short-lived. Unfortunately during the startup phase of the guest OS the balloon driver will not be loaded and this situation can lead to compressing (10% of configured memory) and swapping useless data straight to disk. ESXTOP will display swapped out memory but due to the nature of the data will show little to none swap-in. ESX 4.1 uses a new technique called zero-page sharing. An in-depth post about this cool new technique will follow shortly. **End-note** This post concludes the three-part series about the impact of oversized virtual machines. The reason I wrote these articles is that I know many organizations still size their virtual machines on assumed peak loads happing somewhere in the (late) future of that service or application. Many organizations are using the same policy or method used for physical machines. The beauty of using virtual machines is the flexibility an organization has when it comes to determining the size of a machine during its lifecycle. Leverage these mechanisms and incorporate this in your service catalog and daily operations. Size the virtual machine according to its current or near-future workload.
