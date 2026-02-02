---
title: "Re: impact of large pages on consolidation ratios"
date: 2011-01-25
categories: 
  - "memory"
---

Gabe wrote an article about the [impact of large pages on the consolidation ratio](http://www.gabesvirtualworld.com/large-pages-transparent-page-sharing-and-how-they-influence-the-consolidation-ratio/?utm_source=twitterfeed&utm_medium=twitter), I want to make something clear before the wrong conclusions are being made. Large pages will be broken down if memory pressure occurs in the system. If no memory pressure is detected on the host, i.e the demand is lower than the memory available, the ESX host will try to leverage large pages to have the best performance. Just calculate how big the Translation lookaside Buffer (TLB)is when a 2GB virtual machine use small pages (2048MB/4KB=512.000) or when using large pages 2048MB/2.048MB =1000. The VMkernel need to traverse the TLB through all these pages. And this is only for one virtual machine, imagine if there are 50 VMs running on the host. Like ballooning and compressing, if there is no need to over-manage memory than ESX will not do it as it generates unnecessary load. Using Large pages shows a different memory usage level, but there is nothing to worry about. If memory demand exceeds the availability of memory, the VMkernel will resort to share-before-swap and compress-before-swap. Resulting in collapsed pages and reducing the memory pressure.
