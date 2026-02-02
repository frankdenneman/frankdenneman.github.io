---
title: "Node Interleaving: Enable or Disable?"
date: 2010-12-28
categories: 
  - "numa"
  - "vmware"
tags: 
  - "node-interleaving"
  - "numa"
  - "vmware"
---

There seems to be a lot of confusion about this BIOS setting, I receive lots of questions on whether to enable or disable Node interleaving. I guess the term “_enable_” make people think it some sort of performance enhancement. Unfortunately the opposite is true and it is strongly recommended to keep the default setting and leave Node Interleaving disabled.

**Node interleaving option only on NUMA architectures** The node interleaving option exists on servers with a non-uniform memory access (NUMA) system architecture. The Intel Nehalem and AMD Opteron are both NUMA architectures. In a NUMA architecture multiple nodes exists. Each node contains a CPU and memory and is connected via a NUMA interconnect. A pCPU will use its onboard memory controller to access its own “local” memory and connects to the remaining “remote” memory via an interconnect. As a result of the different locations memory can exists, this system experiences “non-uniform” memory access time.

**Node interleaving disabled equals NUMA** By using the default setting of Node Interleaving (disabled), the system will build a _System Resource Allocation Table_ (SRAT). ESX uses the SRAT to understand which memory bank is local to a pCPU and tries\* to allocate local memory to each vCPU of the virtual machine. By using local memory, the CPU can use its own memory controller and does not have to compete for access to the shared interconnect (bandwidth) and reduce the amount of hops to access memory (latency) [![](images/NUMA.png "NUMA")](http://frankdenneman.nl/wp-content/uploads/2010/12/NUMA.png) \* If the local memory is full, ESX will resort in storing memory on remote memory because this will always be faster than swapping it out to disk.

**Node interleaving enabled equals UMA** If Node interleaving is enabled, no SRAT will be built by the system and ESX will be unaware of the underlying physical architecture. [![](images/UMA.png "UMA")](http://frankdenneman.nl/wp-content/uploads/2010/12/UMA.png) ESX will treat the server as a uniform memory access (UMA) system and perceives the available memory as one contiguous area. Introducing the possibility of storing memory pages in remote memory, forcing the pCPU to transfer data over the NUMA interconnect each time the virtual machine wants to access memory.

By leaving the setting Node Interleaving to disabled, ESX can use System Resource Allocation Table to the select the most optimal placement of memory pages for the virtual machines. Therefore it’s recommended to leave this setting to disabled even when it does sound that you are preventing the system to run more optimally.

Get notification of these blogs postings and more DRS and Storage DRS information by following me on Twitter: [@frankdenneman](https://twitter.com/FrankDenneman)
