---
title: "DRS Migration Threshold in vSphere 7"
date: 2020-05-08
categories: 
  - "drs"
tags: 
  - "drs"
  - "vmware"
  - "vsphere7"
---

DRS in vSphere 7 is equipped with a new algorithm. The old algorithm measured the load of each host in the cluster and tried to keep the difference in workload within a specific range. And that range, the target host load standard deviation, was tuned via the migration threshold.  

The new algorithm is designed to find an efficient host for the VM that can provide the resources the workload demand while considering the potential behavior of other workloads. Throughout a series of articles, I will explain the actions of the algorithm in more detail.  

Due to the changes, the behavior of the migration threshold changed as well. In general, the migration threshold still acts as the metaphorical gas pedal. By sliding it to the right, you press the gas pedal to the floor. You tell DRS to become more aggressive, to reduce or relax certain thresholds. Underneath the covers, things changed a lot. There is no host load standard deviation to compare, but DRS needs to understand workload demand change and how much host inefficiency to tolerate. Let's take a look closer: 

**Migration Threshold** 

Other than greatly improving the text describing each migration threshold, the appearance and behavior of the Migration Threshold (MT) have not changed much in vSphere 7. By default, the slider is set to the moderate "3" setting. There are two more aggressive load-balance settings, 4, and 5. 5 Being the most aggressive. To the left of the default, there are two settings, 1 and 2. However, only setting 2 generates load-balancing recommendations. If you set the slider to 1, the most conservative option, DRS only produces migration recommendations that are considered mandatory.  Mandatory moves are generated for a few events, the three common reasons are when the host is placed into maintenance mode, when a proactive HA evacuation occurs, or when a VM violates an (anti-) affinity rule.  The remainder of the article describes the setting of the sliders by referring to the numbers.  

**Selecting the Appropriate Migration Threshold Setting** 

MT setting 2 is intended for a cluster with mostly stable workloads. Stable in the sense of workload variation, not failure rates ;). When workload generates a continuous workload, it makes less sense to move workload aggressively around. MT 3 is a healthy mix of stable and bursty workloads, while MT 4 and MT5 are designed to react to workloads spikes and bursts.

![](images/Migration-Threshold-3.png)

**Headroom threshold** 

To influence balancing moves, DRS uses a threshold that identifies a particular level of headroom (used capacity) within a host. To point out, this is not a strict admission control function.  

The threshold identifies a point where overall host utilization starts to introduce (some) performance loss to the associated workloads on the host. As the new DRS algorithm is designed to consider VM demand, it is focused on finding the best host possible. DRS compares the overall host utilization of each host and migrates VMs to help workloads have enough room to burst.  

By default, DRS starts to consider the host less efficient when the host load exceeds 50%. Once the threshold is surpassed, DRS examines possible migrations to help find workloads a more efficient host. Similar to the old algorithm, the cost of the migration needs to exceed the improvement of efficiency.  When you select a more aggressive migration threshold setting (MT4, MT5), the tolerance for host load is lowered to 30%. From that point on, DRS will take a particular level of inefficiency into account and starts to analyze other hosts to understand whether specific workloads will benefit from placement on another host.  Another way to put it is that DRS attempts to provide 70% headroom in this situation. As a result, you will notice more workload migrations when selecting MT4 or MT5.  

![](images/2-Headroom-Threshold.svg)

**Demand** **Estimation** 

To find an efficient host, DRS needs to understand the demand of the vSphere Pod or the VM. DRS uses a number of stats to get a proper understanding of the workload demand. These stats are provided by the ESXi hosts. DRS is designed to be conservative as it doesn't want to move a virtual machine based on an isolated event. Taking care of a sudden increase in demand is the role of the ESXi host. When this becomes structural behavior, then it's DRS task to find the right spot for this VM.  

_Please note that a vSphere pod will not be migrated. Although DRS does not load-balance vSphere pods to get a better overall capacity usage, it will keep track of the vSphere Pods demand since it could affect the performance of other workloads (VMs and pods) running on the host._ For more info about vSphere pods, please read the article "[Initial Placement of a vSphere Pod](https://frankdenneman.nl/2020/03/06/initial-placement-of-a-vsphere-native-pod/)".

By default, DRS calculates an average demand of over 40 minutes for each workload. This period depends on the VM memory configuration and the migration threshold. We learned that DRS needs to use a shorter history for smaller VMs to better catch the behavior of vSphere pods or VMs with a smaller memory footprint. Below is an overview of the Migration Threshold settings and the number of minutes used to determine the demand for each workload. 

![](images/3-Lookback-window-for-stats.svg)

**Cost-Benefit** 

DRS needs to consider the state of the cluster, the workload demand of all the vSphere pods and the VMs, and it needs to ensure that whatever it does, does not interfere with the primary goal of the virtual infrastructure, and that is providing resources to workloads. Every move made consumes CPU resources. It absorbs bandwidth, and in some cases, can affect memory sharing benefits. DRS must weigh all the possibilities. With DRS in vSphere 7 that functionality is called cost-benefit filtering. Moving the migration threshold to the right reduces certain cost filtering aspects while relaxing some benefit requirements. This allows DRS to become more responsive to bursts.  As a result, you will notice more workload migrations when selecting MT4 or MT5.  

**DRS Responsibility** 

Please remember that vSphere consists of many layers of schedulers all working closely together. DRS is responsible for placement, finding the best host for that particular vSphere pod or VM. However, it is the responsibility of the actual ESXi host schedulers to ensure the workload gets scheduled on the physical resources. Consider DRS as the host or hostess of the restaurant, escorting you to a suitable table, while the ESXi schedulers are the cooks and the waiters.  

Individual workload behavior can change quite suddenly, or there is an abrupt change in resource availability. DRS needs to coordinate and balance all the workloads and their behavior in any possible scenario. The new DRS algorithm is completely redesigned, and I think it's an incredible step forward.  

But a new algorithm, with new tweakable parameters, also means that we can expect different behavior. It's expected that you will see more vMotions compared to the old algorithm, regardless of MT selection. A future article will explain the selection process of the algorithm. As always, it's recommended to test the new software in a controlled environment. Get to understand its behavior and test out which migration threshold fits your workload best.
