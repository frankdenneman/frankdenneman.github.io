---
title: "A vSphere Focused Guide to the Intel Xeon Scalable Family"
date: 2017-09-26
categories: 
  - "numa"
  - "vmware"
---

Intel released the much-anticipated Skylake Server CPU this year. Moving away from the E5-2600-v moniker, Intel names the new iteration of its server CPU the Intel Xeon Scalable Family. On top of this it uses precious metal categories such as Platinum and Gold to identify different types and abilities.

Upholding the tradition, the new Xeon family contains more cores than the previous Xeon version. The new top-of-the-line CPU offers 28 cores on a single processor die, memory speeds are now supported up to 2666 MHz. However, the biggest appeal for vSphere datacenters is the new "Purley" platform and its focus on increasing bandwidth between possibly every component possible. In this series, we are going to look at the new Intel Xeon Scalable family microarchitecture and which functions help to advance vSphere datacenters.

**NUMA and vNUMA Focus** Instead of solely listing the speeds and feeds of the new architecture, I will be reviewing the new functionality with considerations of today's vSphere VM configuration landscape. In modern vSphere datacenters, small VMs and large VMs co-exists with a single server. Many VMs consume the interconnect between physical CPUs. Some VMs span multiple NUMA nodes (Wide-VMs) while others fit inside a single physical NUMA node. The VMkernel NUMA scheduler attempts to optimize local memory consumption as much as possible. Sometimes remote memory is unavoidable. Consolidation ratios increase each year, hence the focus on the interconnect. Yet, single-threaded applications are still prevalent in many DC's. Therefore single-core improvements will not be ignored in this series. Designing a system that is bound to run a high consolidation with a mix of small and large VMs is not an easy task.

**Rebranding** The Xeon Scalable family introduces a new naming scheme. Gone are the names such as the E5-2630 v4, E5-4660 v4 or E7-8894 v4. Now Bronze, Silver, Gold, and Platinum class indicate the range of overall performance, Bronze representing the entry-level class CPU comparable to the previous E3 series, while Platinum class CPUs provide you the highest levels of scalability and most cores possible. As of today, Intel offers 58 different CPU types within the Xeon Scalable family, i.e., 2 Bronze CPUs, 8 Silver, 6 Gold 51xx, 26 Gold 61xx and 16 Platinum CPUs.

|  | [Bronze](https://ark.intel.com/compare/123540,123546) | [Silver](https://ark.intel.com/compare/126155,120481,126153,123550,123547,123551,123549,123544) | [Gold 51xx](https://ark.intel.com/compare/120475,120477,120474,126154,120473,120484) | [Gold 61xx](https://ark.intel.com/compare/120495,120491,120490,123690,120489,124942,124943,120488,123685,120487,120485,120486,123542,123686,120476,120479,120494,120493,123541,123545,123688,120492,120482,123548,123689,120483) | [Platinum](https://ark.intel.com/compare/120498,120496,120505,125056,120508,120507,120506,120504,120503,123543,120502,123687,120501,120500,120499,120497) |
| --- | --- | --- | --- | --- | --- |
| Scalability | 2 | 2 | 2 | 2-4 | 2-8 |
| Max Cores | 8 | 12 | 14 | 22 | 28 |
| Max Base Frequency (GHz) | 1.7 | 2.6 | 3.6 | 3.5 | 3.6 |
| Max Memory Speed (MHz) | 2133 | 2400 | 2400 | 2666 | 2666 |
| UPI\* Links | 2 | 2 | 2 | 3 | 3 |
| UPI Speed (GT/s) | 9.6 | 9.6 | 10.4 | 10.4 | 10.4 |

\* The Xeon Scalable family introduces a new processor interconnect called the UltraPath Interconnect (UPI) and replaces the QuickPath Interconnect. The next article in this series provides an in-depth look at the UPI.

**Integrations and Optimizations** Intel uses suffixes to indicate particular integrations or optimizations.

| Suffix | Function | Integration \| Optimization | Availability |
| --- | --- | --- | --- |
| [F](https://ark.intel.com/compare/123689,123688,123686,123685,123690,123687,125056) | Fabric | Integrated Intel® Omni-Path Architecture | Gold 61xx, Platinum |
| [M](https://ark.intel.com/compare/120494,120486,120488,120502,120507,120505) | Memory Capacity | 1.5 TB Support per Socket | Gold 61xx, Platinum |
| [T](https://ark.intel.com/compare/123549,126153,126155,126154,120477,123548,123545,123542,123543) | High Tcase | Extended Reliability (10-Year Use) | Silver,Gold, Platinum |

**Omni-Path Architecture** The new Xeon family offers on-die Omni-Path Architecture that allows for 100 Gbps connectivity. In-line with the industry effort to remove as much "moving parts or components as possible the new architecture the signal is not being routed through the socket and motherboard but provides a direct connection to the processor.

\[caption id="attachment\_7085" align="aligncenter" width="676"\][![](images/Intel-Xeon-Scalable-Fabric-v-No-Fabric-750x460.jpg)](http://frankdenneman.nl/wp-content/uploads/2017/09/Intel-Xeon-Scalable-Fabric-v-No-Fabric.jpg) Image by ServeTheHome.com\[/caption\]

The always excellent [Serve The Home](https://www.servethehome.com/intel-skylake-omni-path-fabric-does-not-work-on-every-server-and-motherboard/) has published a nice article about the F-type Xeons. Unfortunately, the current vSphere version does not support the Omni-Path Architecture.

**Total Addressable Memory** Intel hard-coded the addressable memory capacity on the CPU. As a result, non-M CPUs will not function if more than 768 GB of RAM is present in the DIMM sockets connected to its memory controllers. If you tend to scale-up your servers during their lifecycle, consider this limitation. If you are planning to run monster VMs that require more than 768 GB of RAM and want to avoid spanning it across NUMA nodes, consider obtaining "M" designation CPUs.

Why wouldn't you just buy M designated CPUs in the first place, you might wonder? Well, the M badge comes with a [near-3K USD price hike](https://ark.intel.com/compare/120487,120488,120485,120486). Comparing, 6142 (16 cores at 2.6 GHz) and 6140 (18 cores at 2.3 GHz) the list price for the 6142 is $2946, while the 6142M is $5949. The similar price difference for the 6140, vanilla style 6140 costs $2445, M-badge $5448. But with current RAM prices, we are talking about a minimum of $100.000 price tag for 1.5 TB of memory PER socket!

**Extended Reliability** For specific use-cases, Intel provides CPUs with an extended reliability of up to 10 years. As you can imagine, these CPUs do not operate at top speeds. The fastest T enabled CPU runs at 2.6 GHz base frequency.

**Similar, but not identical CPU packaging** When reviewing the spectrum of available CPUs, one noticeable thing is the availability of identical core count CPUs across the precious metals. For example, the 12 core CPU package. It's available in Silver, Gold 51xx, Gold 61xx and Platinum. It's available with an extended Tcase (Intel Xeon Silver 4116), and the Intel Xeon Gold 6126 is also available as 6126T and 6126F. One has to dig a little bit further to determine the added benefits of selecting a Gold version over a Silver version.

| Processor | Silver 4116 | Gold 5118 | Gold 6126 | Gold 6136 | Gold 6146 | Platinum 8158 |
| --- | --- | --- | --- | --- | --- | --- |
| Cores | 12 | 12 | 12 | 12 | 12 | 12 |
| Base Frequency (GHz) | 2.10 | 2.30 | 2.60 | 3.00 | 3.20 | 3.00 |
| Max Turbo Frequency (GHz) | 3.00 | 3.20 | 3.70 | 3.70 | 4.20 | 3.70 |
| TDP (W) | 85 | 105 | 125 | 150 | 165 | 150 |
| L3 Cache (MB) | 16.5 | 16.5 | 19.25 | 24.75 | 24.75 | 24.75 |
| \# of UPI Links | 2 | 2 | 3 | 3 | 3 | 3 |
| Scalability | 2S | 4S | 4S | 4S | 4S | 8S |
| \# of AVX-512 FMA Units | 1 | 1 | 2 | 2 | 2 | 2 |
| Max Memory Size (GB) | 768 | 768 | 768 | 768 | 768 | 768 |
| Max Memory Speed (MHz) | 2400 | 2400 | 2666 | 2666 | 2666 | 2666 |
| Memory Channels | 6 | 6 | 6 | 6 | 6 | 6 |

[Part 2: Memory Subsystem available](http://frankdenneman.nl/2017/10/03/vsphere-focused-guide-intel-xeon-scalable-family-memory-subsystem/)
