---
title: "vSphere 6.5+ DRS Pairwise Balancing"
date: 2019-10-30
categories: 
  - "drs"
  - "vmware"
coverImage: "rundrs.png"
---

Or maybe I should have called this blog post, "I'm seeing an excessive number of DRS initiated vMotions on my newly upgraded 6.5 environment". Recently I was part of a few conversations about the nature of DRS load balancing in systems running vSphere 6.5 and newer. It was noticed that more vMotion operations where occurring since running 6.5 and it's highly likely that these operations occur due to the new DRS pairwise balancing functionality. Pairwise balancing was introduced by vSphere 6.5 and is focused on keeping the host resource utilization disparity within a certain threshold. As a result, DRS performs load-balancing operations if the difference between the lowest-utilized host and the highest-utilized host is a certain percentage. That percentage depends on your migration threshold. The default migration threshold uses a 20% tolerable difference in utilization.

| **Migration Threshold Level** | **Tolerable CPU/Memory usage difference between any two hosts in the cluster** |
| --- | --- |
| 1 | Not Available (only Affinity violations and MM migrations allowed) |
| 2 | 30% |
| 3 (Default migration threshold) | 20% |
| 4 | 10% |
| 5 | 5% |

This new feature is needed as clusters keep on growing larger and larger. To determine if load-balancing operations are necessary, DRS calculates two metrics, the current host load standard deviation (CHLSTD) and the target host load standard deviation (THLSTD). Each host reports its load and DRS calculates the standard deviation of the host load metric across all the hosts in the cluster. DRS calculates a target host load balance for the cluster and as long as the current host load standard deviation is less than or equal to the target host load value, DRS will consider the cluster balanced. The migration threshold allows how far apart the CHLSTD and THLSTD before it triggers load balancing operations. The higher the aggressiveness of the migration threshold, the lower the difference between the CHLSTD and THLSTD is tolerated. 

A situation can occur that a few hosts in a large cluster can experience a high resource utilization, while the majority of hosts are not. Due to the size of the cluster, the few high host load become just some statistical outliers than simply disappear as noise due to the vast number of hosts that experience (far) lower utilization. As a result, these outliers are missed as the calculate CHLSTD is below the threshold required to trigger load balancing.

By adding the functionality of pairwise balancing, and "simply" comparing the highest reported utilization with the lowest utilization, these outliers might be a thing of the past. That means that in certain cases, the DRS UI might report that the cluster is in a balanced state, yet load-balance operations still occur. This behavior can be attributed to pairwise balancing.

Please keep in mind that if you are using a migration threshold that is more aggressive than the default setting, the tolerable difference between hosts is reduced, more migrations are likely to occur.

So what happens when the tolerable difference is detected in the cluster? Does this mean that VMs are migrated from the highest utilized host to the lowest utilized host? Not necessarily. VMs can be migrated to any other host in the cluster. DRS still takes many different requirements into account when selecting a virtual machine migration for load-balancing purposes. Anti-affinity and affinity rules cannot be violated to obtain a better cluster load-balance, so these moves are not considered. Compatibility of hosts and VM configuration also impact migration options (typically a missing datastore or network portgroup are common reasons why particular hosts are overloaded and why other hosts are lower utilized), but also the "cost-benefit" of a VM migration is still taken into account. It still needs to make sense for the cluster balance to incur infrastructure costs and risk to move a particular VM.

If you recently updated your vCenter to 6.5/6.7 and are curious to see whether the vMotions are triggered due to Pairwise imbalance operations, you can use the online version of the DRS Dump Insight tool available at [https://www.drsdumpinsight.vmware.com/](https://www.drsdumpinsight.vmware.com/). You can also run the DRS dump insight tool on-prem by installing one of the flings available here: [https://flings.vmware.com/?utf8=%E2%9C%93&q=DRS+Dump+Insight&button=](https://flings.vmware.com/?utf8=%E2%9C%93&q=DRS+Dump+Insight&button=). Grep for "Pairwise Imbalance".

If this behavior is not appreciated, and you do not want to alter the migration threshold, you can switch back to the old behavior by turning off pair-wise balancing by setting the cluster advanced option "CheckPairWiseImbalance to 0. (case-sensitive). Although this functionality was introduced by vSphere 6.5 and is active by default in all newer releases, we have backported this functionality to vSphere 6.0 u3.

One thing I would like to ask if you want to disable it, what are the reasons? I expect "too much vMotions", but I would like to understand why a vMotion or a collection of vMotions is considered not desirable? The main goal is to get the VMs to a place where they have access to enough resources, why is that still a bad thing?
