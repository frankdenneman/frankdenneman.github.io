---
title: "Introduction 2016 NUMA Deep Dive Series"
date: 2016-07-06
categories: 
  - "numa"
  - "vmware"
---

Recently I've been analyzing traffic to my site and it appears that a lot CPU and memory articles are still very popular. Even my [first article](http://frankdenneman.nl/2010/02/03/sizing-vms-and-numa-nodes/) about NUMA published in february 2010 is still in high demand. And although you see a lot of talk about the upper levels and overlay technology today, the focus on proper host design and management remains. After all, it's the correct selection and configuration of these physical components that produces a consistent high performing platform. And it's this platform that lays the foundation for the higher services and increased consolidating ratios.

Most of my NUMA content published throughout the years is still applicable to the modern datacenter, yet I believe the content should be refreshed and expanded with the advancements that are made in the software and hardware layers since 2009.

To avoid ambiguity, this deep dive is geared towards configuring and deploying dual socket systems using recent Intel Xeon server processors. After analyzing the dataset of more than 25.000 ESXi host configurations collected from virtual datacenters worldwide, we discovered that more than [80% of ESXi host configuration](http://frankdenneman.nl/2016/02/15/insights-into-vm-density/) are dual socket systems. Today, according to IDC, Intel controls 99 percent of the server chip market. Despite the strong focus of this series on the Xeon E5 processor in a dual socket setup, the VMkernel, and VM content is applicable to systems running AMD processors or multiprocessor systems. No additional research was done on AMD hardware configurations or performance impact when using high-density CPU configurations.

#### The 2016 NUMA Deep Dive Series

The 2016 NUMA Deep Dive Series consists of 7 parts.The 2016 NUMA deep dive series is split into three main categories; Physical, VMkernel, and Virtual Machine.

**Part 1: [From UMA to NUMA](http://frankdenneman.nl/2016/07/07/numa-deep-dive-part-1-uma-numa/)** Part 1 covers the history of multi-processor system design and clarifies why modern NUMA systems cannot behave as UMA systems anymore.

**Part 2: [System Architecture](http://frankdenneman.nl/2016/07/08/numa-deep-dive-part-2-system-architecture/)** The system architecture part covers the Intel Xeon microarchitecture and zooms in on the Uncore. Primarily focusing on Uncore frequency management and QPI design decisions.

**Part 3: [Cache Coherency](http://frankdenneman.nl/2016/07/11/numa-deep-dive-part-3-cache-coherency/)** The unsung hero of today's NUMA architecture. Part 3 zooms in to cache coherency protocols and the importance of selection the proper snoop mode.

**Part 4: [Local Memory Optimization](http://frankdenneman.nl/2016/07/13/numa-deep-dive-4-local-memory-optimization/)** Memory density impacts the overall performance of the NUMA system, part 4 dives into the intricacy of channel balance and DIMM per Channel configuration.

**Part 5: [ESXi VMkernel NUMA Constructs](http://frankdenneman.nl/2016/08/22/numa-deep-dive-part-5-esxi-vmkernel-numa-constructs/)** The VMkernel has to distribute the virtual machines to provide the best performance. This part explores the NUMA constructs that are subject to initial placement and load-balancing operations.

**Part 6: NUMA Initial Placement and Load Balancing Operations** The VMkernel has to distribute the virtual machines to provide the best performance. This part explores the NUMA initial placement and load-balancing operations. (not yet released)

**Part 7: From NUMA to UMA** The world of IT moves in loops of iteration, the last 15 years we moved from UMA to NUMA systems, which today's focus on latency and the looming licensing pressure, some forward-thinking architects are looking into creating high performing UMA systems. (not yet released)

The articles will be published on a daily basis to avoid saturation. Similar to other deep dives, the articles are lengthy and contain lots of detail. Up next, [Part 1: From UMA to NUMA](http://frankdenneman.nl/2016/07/07/numa-deep-dive-part-1-uma-numa/)
