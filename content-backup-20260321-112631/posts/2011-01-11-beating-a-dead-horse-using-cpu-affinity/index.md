---
title: "Beating a dead horse - using CPU affinity"
date: 2011-01-11
categories: 
  - "cpu"
tags: 
  - "cpu-affinity"
  - "numa"
  - "vmware"
---

Lately the question about setting CPU affinity is rearing its ugly head again. Will it offer performance advantages for the virtual machine? Yes it can, but only in very specific cases. Additional settings and changes to the virtual infrastructure are required to obtain a performance increase over the default scheduling techniques. Setting CPU affinity by itself will not result in any performance gain, but usually a performance decrease.

**What does CPU affinity do?** By setting a CPU affinity on the virtual machine you are **limiting** the available CPUs on which the virtual machine can run. It does not dedicate that CPU to that virtual machine and therefore does not restrict the CPU scheduler from using that CPU for other virtual machines.

**When will CPU-affinity help?** Under a controlled environment some specific workloads can benefit from using CPU affinity. When the virtual machine workload is cache bound and has a larger cache footprint than the available cache of one CPU it can profit from aggregated caches. However, if this workload has high intra-thread communications and is running on specific CPU architectures setting CPU affinity can have the opposite effect and become detrimental to the performance of the application.

CPU-affinity can also be used to isolate a physical CPU to a virtual CPU. But requires a lot of changes and increases management. It will never dedicate the physical CPU to the virtual machine as the VMkernel schedules all its processes across all available CPUs regardless of any custom setting a virtual machine has. Furthermore the scheduling overhead stays the same whether CPU-affinity is set on the virtual machine or not.

To determine if you application fit this description can be a challenge and maintaining such configurations usually result in a nightmare. Generally CPU-affinity is only used for simulations and load testing and it is better left unused for every other cases. Setting CPU-affinity results in less choice for the CPU scheduler to schedule the virtual machine, but there is more to it as well:

**Controlled environment** Already mentioned but this cannot be stressed enough, CPU affinity does not equal isolation of a physical CPU. In other words, when a virtual machine is pinned to a physical CPU it does not control or own that CPU. The VMkernel CPU scheduler still considers that physical CPU a valid CPU to schedule other virtual machines on. If isolation of a CPU is the end-goal, than all other residing virtual machines on the host (and virtual machine that will be created in the future) must be configured with CPU affinity as well and the specific CPU(s) assigned to the virtual machine must excluded from all other virtual machines.

Setting CPU affinity results in manual CPU micro management and can be a nightmare to maintain. To make it worse, think of the impact a migration will have, the administrator needs to configure the virtual machines on the destination host to exclude the CPU from all active virtual machines as well.

_(**Update: Recent vSphere versions offer the "Latency Sensitive" functionality, isolating cores for vCPUs)**_

**Virtual Machine worlds** A virtual machine is made of multiple worlds (threads), besides the vCPU world, worlds are active for the virtual machine MKS subsystem, CD-ROM and VMX file. Although the vCPU world generates the greater part of the CPU load, sometimes a physical CPU is required to run the other worlds. If CPU affinity is set, then all the worlds that constitute the virtual machine can only run on the specified CPUs. If set incorrectly, it can reduce the throughput of the virtual machine as the worlds must compete between each other for CPU time. Therefore it is recommended to add an additional CPU for these worlds. For example; configure a CPU affinity setting that contains 3 physical CPUs for a 2 vCPU virtual machine.

**Resource entitlements** As CPU affinity will not automatically isolate the CPU for that specific virtual machine, shares and reservations needs to be set to guarantee a specific performance level. Because the scheduler will attempt to maintain fairness for all virtual machines it is possible that other virtual machines will be scheduled on the set of CPU specified in the affinity set of the virtual machine. Adjust the shares and reservations of the virtual machine accordingly to ensure priority over other active virtual machines. Be aware that CPU reservations are friendly; although the vCPU is guaranteed a specific portion of physical resources, it might happen that an external thread/interloper (other virtual machine) is using the vCPU; this thread will not instantly be de-scheduled. Even when the waiting virtual machine has a 100% CPU reservation configured.

To make it worse, in the case when multiple virtual machines are affinity-bound to the same processor it is possible that the CPU scheduler cannot meet the specified reservation. Be aware that admission control ignores affinity, so multiple virtual machines can have a full reservation equal to a full core but still need to compete with other affinity bound virtual machines. More information about how CPU reservations work can be found in the article: “[Reservations and CPU Scheduling](http://frankdenneman.nl/2010/06/reservations-and-cpu-scheduling/)”.

**CPU reservations and HA admission control** If the virtual machine with the reservation is running in a HA cluster with a “Host failures cluster tolerates” admission control policy, the CPU reservation will influence the Slot size of the Cluster and can therefore impact the consolidation ratio of the cluster. More info about slot-sizes can be found on the [HA deepdive](http://www.yellow-bricks.com/vmware-high-availability-deepdiv/).

**CPU affinity and DRS clusters.** Because vMotion is not allowed if a virtual machine is configured with CPU affinity, that virtual machine cannot be placed in a DRS cluster with automation mode set to fully automated. If a virtual machine needs to be configured with CPU affinity, the administrator has three choices:

- Place the virtual machine on a stand-alone host

- Set DRS automation level to manual / partially automated

- Set virtual machine automation mode to manual / partially automated

**Stand-alone host** If the virtual machine is placed on the stand-alone host the performance of the virtual machine depends on the level of contention and the virtual machine resource entitlement. During resource contention it can only fall back on its resource entitlement and hopefully gain a higher priority than the other residing virtual machines. If the virtual machine was located on an ESXi host in a DRS cluster, the virtual machine could have been migrated to receive its resource entitlement on another host. By choosing CPU-affinity, you are betting only on one horse, the local CPU scheduler of one host instead of leveraging the full suite of resource management vSphere delivers today.

**DRS set to Manual or partially automated** If the DRS automation level is set to manual or partially automated, the cluster will not automatically load balance virtual machines and DRS will recommend migrations. These recommendations must be applied manually by the administrator. DRS imbalance calculation will be invoked every 300 seconds but is also triggered if the cluster detects resource demand and supply changes, as well as changes in the resource settings in the cluster. As you can imagine, this behavior will create an incredible load on the administrator to let the cluster operate as efficiently as possible if he wants to ensure that the virtual machines are receiving their resource entitlements.

**Set Virtual machine automation mode to manual / partially automated** By changing the automation mode on VM-level, the virtual machine can still be placed inside a fully automated DRS cluster. Although DRS will not automatically migrate this virtual machine, it can migrate other virtual machines to ensure every virtual machine will receive its resource entitlement. However additional measures (shares and reservations) must be taken to guarantee the virtual machine enough physical resources.

**CPU architectures** Today new CPU architectures, such as the Intel Nehalem and AMD Opteron’s offer a variety of on-die caches, multiple cores \\ logical CPUs and an optimized local\\remote memory subsystem. These features can either helpful or be detrimental to the performance of a virtual machine with CPU affinity.

**Cache level** If a virtual machine is spanned across two processors (packages) it effectively results in having two L3 caches available to the virtual machine. Today’s CPU architectures offer dedicated L1 and L2 cache per core and a shared last-level L3 cache for all cores inside the CPU package. Because access to Last level cache is faster than (normal) memory, it makes sense to span the virtual machine across two processor packages to increase the amount of available L3 cache.

However the inter-socket communication speed can reduce –or remove- the positive effect of having low-latency cache available and if the workload can fit inside one cache (small cache footprint) and uses intensive intra-thread communication, than placement in one processor packaged is to be preferred over spanning multiple packages.

**HyperThreading** If a virtual machine is running on a HyperThreading-enabled system it is best to set the CPU-affinity to logical CPUs not belonging to the same core. The HT threads on a core are translated by the VMkernel as logical CPUs and are consecutively numbers, for example Core 1 contains LCPU0 and LCPU1, Core 2 contains LCPU2 and LCPU3, etc. If CPU-affinity is set to logical CPUs belonging to the same core, both vCPUs of the virtual machine need to compete with each other for physical CPU resources. By scheduling a virtual machine on logical CPUs of different cores, it doesn’t have to compete and can benefit the vCPUs’ throughput because the VMkernel allows the vCPU to use the entire Cores’ resources if only one logical CPU residing on the core is active.

[![](images/cpu-affinity-HT.png "cpu-affinity-HT")](http://frankdenneman.nl/wp-content/uploads/2011/01/cpu-affinity-HT.png)

**NUMA** If CPU affinity is set on a virtual machine running in a NUMA architecture (Intel Nehalem and AMD Opteron) the virtual machine is treated as a NON-NUMA client and gets excluded from NUMA scheduling. Therefore the NUMA scheduler will not set a memory affinity for the virtual machine to its current NUMA node and the VMkernel can allocate memory from every available NUMA node in the system Therefore the virtual machine may end up running on a different NUMA node than were its memory is residing, resulting in unnecessary memory latency and possibly higher %Ready time as the instruction must wait until the memory is fetched from a remote node.

**Bottomline** The bottomline is that almost in every case CPU affinity is better left unused. Scheduling threads is very complex, scheduling threads belonging to multiple virtual machines with different priorities, activity, progress and still considering optimal use of the underlying CPU and memory architecture is mind-blowing complex. The CPU scheduler is aware of all these components and together with the global scheduler (DRS) it can see to it that the virtual machine will receive its resource entitlement. If the virtual machine must have access to physical resources at any time, other mechanisms such as resource allocation settings will have a better effect than using the advanced setting CPU-affinity.
