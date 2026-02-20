---
title: "How vSphere GPU Modes and Assignment Policies Determine Host Level Placement"
date: 2026-02-17T14:00:00+01:00
draft: false
categories: ["ai"]
tags: ["GPU Placement", "AI Platform", "VMware Private AI Foundation", "Kubernetes", "vSphere", "Scheduling"]

series: ["Architecting AI Infrastructure"]
series_order: 4
---

## Architecting AI Infrastructure - Part 4

In the [last article](https://frankdenneman.nl/posts/2026-02-13-how-vsphere-drs-makes-gpu-placement-decisions/), we tracked a GPU-backed VM from resource configuration to host selection. DRS evaluated the cluster, Assignable Hardware filtered hosts for GPU compatibility, DRS ran its Goodness calculation, and picked a destination host. Now, the host is selected. But the placement is not finished.

Inside the host, another set of decisions decides which physical GPU gets the workload and what types of workloads that GPU will handle from then on. These host-level choices are less visible than DRS decisions. They do not show up in dashboards or trigger alerts. However, their effects add up over time, and they play a key role in keeping a shared AI platform healthy or letting it decline.

## What AI Workloads Actually Ask of a GPU

Most AI workloads fall into four main GPU usage patterns.

Passthrough lets one virtual machine use one physical GPU directly as a PCI device. This setup is used when software requires bare-metal-level GPU access or when a workload is a specialized appliance with a fixed GPU configuration. The rule is simple: one VM, one GPU, no sharing. The trade-offs are no vMotion, no DRS load balancing, and no automatic HA recovery if static direct path IO is used.

Fractional GPU splits a physical GPU so that several virtual machines can share it simultaneously, each with its own memory and limited compute power. Embedding models, reranker services, and Jupyter notebooks often use this setup. For example, an embedding model usually needs 4 to 20GB of GPU memory, and a notebook uses the GPU in short bursts between long waits for data. Neither needs a full 80GB H100. A fractional profile gives each workload what it needs: dedicated memory, limited compute, and a resource shape the platform can manage for many users at once. This article focuses on this shape, its setup options, and the fragmentation it can cause.

Full GPU gives one virtual machine full access to a physical GPU using a full-size vGPU profile. Unlike passthrough, this setup still allows vMotion, DRS, and HA recovery. It is used for production inference services for large models, and fine-tuning runs that use most of the GPU's memory. Full GPU use has stricter placement limits than fractional GPU use, since each use takes up an entire device.

Multi-GPU gives a single virtual machine access to several physical GPUs, connected via NVLink or NVSwitch for fast communication. This is not just a bigger version of single-GPU use; it is a different shape in which the interconnect topology is part of the resource contract. This setup is used for fine-tuning and inference on the largest production models. Full GPU and multi-GPU placement will be discussed in Part 6.

## The Handoff from DRS to the Host

After DRS picks a host, it hands off the placement to the Assignable Hardware framework. The platform now knows which host will get the virtual machine, but it does not yet know which physical GPU on that host will be used, or whether any are available given their current state.

At this stage, two host-level settings come into play. The first is the GPU Assignment Policy, which controls how virtual machines are spread across the host's physical GPUs. The second is the vGPU Mode, which specifies which profile combination a GPU accepts at any given time. These settings work together to decide where workloads go and how flexible the platform will be for future jobs.

For Kubernetes operators, this is similar to how the scheduler picks a node and the device plugin chooses which GPU to use. In vSphere, the device plugin role is managed by administrator-defined policies. This is not just a first-available match, but a planned way to distribute work across the platform.

The diagram below shows all host and GPU policies and their relationships. Each part will be explained in this series.

![](images/GPU_policies.svg)

## GPU Assignment Policy

The GPU Assignment Policy answers a key question: when a VM lands on a host with several eligible GPUs, which one should it use?

Spread VMs across GPUs does what it promises: spreads VMs across GPUs, placing each new VM on the device with the fewest vGPUs. This keeps the load balanced and prevents any one device from becoming a bottleneck. In the UI, this is also referred to as Best Performance.

Group VMs on GPU until full, does the opposite, filling up one GPU before moving to the next. This keeps as many GPUs as possible in a neutral, unbound state, ready to accept any compatible profile when needed. In the UI, this is also referred to as GPU consolidation.

Please note: the GPU Assignment Policy only applies when the GPU is in Same Size mode. In Mixed Size mode, the host selects the GPU based on availability and profile compatibility, so this setting is ignored.

![](images/GPU_assignment_policy.svg)

The diagram shows a startup order of three VMs: the first two have a 10GB vGPU profile configured, while the third has a 20GB vGPU profile. In the left scenario, the ESXi host is configured with a 'Spread VMs across GPUs' assignment policy, thus VM1 goes to GPU1 and VM2 goes to GPU2. The available GPU memory is still 140 GB, yet VM3 cannot find a compatible GPU in this scenario. Hopefully, another ESXi host in the cluster is either empty or has a 20GB profile active. On the right, the ESXi host is now configured with a 'Group VMs on GPU policy' and VMs 1 and 2 are both placed on GPU 1, VM3 can be powered on, as GPU2 is in a neutral, unbound state. Both scenarios use the 'Same Size' vGPU mode.

## vGPU Mode

vGPU Mode is set for each physical GPU and determines which profiles that GPU accepts at any time. There are two modes in the UI, but one can consider MIG mode as the silent third one. Choosing between these modes is one of the most important decisions when setting up a shared AI platform.

![](images/vgpu_mode.png)

### Same Size: Predictability Through Uniformity

In Same Size mode, a physical GPU starts in a neutral state and can accept any supported vGPU profile. The first virtual machine placed on that GPU sets the profile. After that, the GPU is locked, and every VM must use the same profile. Any request for a different size is rejected, no matter how much capacity is left, until all VMs are powered off and the GPU returns to neutral.

In a controlled environment with a limited and clear set of profiles, this locking is helpful. It enforces a GPU contract and makes usage predictable. Problems appear in self-service setups where placement order is random. For example, if a data scientist starts a workload with a 10C profile on Monday morning, that GPU is locked to 10C until the workload ends. Later, an engineer who needs an 8C slot finds a GPU with 70GB free and six open slots, but none can accept their request. The capacity is there, but the lock prevents its use.

### Mixed Size: Flexibility With Alignment Constraints

Mixed Size mode, added in vSphere 8 Update 3 for Ampere and newer GPUs, removes the locking behavior. In this mode, a GPU can accept profiles of different sizes at the same time. For example, a notebook with a 10C profile and an embedding service with an 8C profile can share the same GPU without blocking each other.

This flexibility comes with one main constraint: placement IDs. A GPU's memory is divided into fixed ranges, and profiles must fit into ranges that match their size. On an 80GB H100, profiles of 10GB, 20GB, and 40GB fit together without leaving unused gaps. Profiles like 8GB or 16GB do not line up with 20GB, so mixing them can leave small gaps that no other profile can use. For example, the H100 supports 4GB, 5GB, 8GB, 10GB, 16GB, 20GB, 40GB, and 80GB profiles. If VM1, VM2, and VM4 use a 16GB profile and VM3 uses a 20GB profile, all VMs can be placed, but VM3 must fit within its placement ID, leaving 12GB unused.

![](images/H100_placement_id.svg)

The platform does not stop these gaps from happening. The key is to choose profiles that both support your workload and align with placement IDs. The [NVIDIA AI Enterprise User Guide](https://docs.nvidia.com/ai-enterprise/5.1/user-guide/index.html#vgpu-types-nvidia-h100-pcie-80gb) is a helpful resource. Sometimes, it is better to use a slightly larger profile, like 20GB instead of 16GB, if it helps support multiple vGPU profiles. If done right, Mixed Size mode gives the most placement flexibility with no locking and no wasted capacity.

### MIG: Hardware Isolation With a Fixed Resource Budget

Multi-Instance GPU mode splits the physical GPU at the hardware level before any workloads start. Each partition gets its own compute and memory slices that no other workload can use. This is not just isolation by software or a scheduler. It is a true hardware partition, so two workloads on the same GPU cannot see or affect each other's resources.

The trade-off is less flexibility. An H100 80GB has seven compute slices and eight memory slices. MIG profiles use these in fixed combinations, and some choices leave compute slices unused. The 3g.40gb profile uses three compute, and four memory slices, so you can fit two per GPU and only one compute slice is left unused. The 4g.40gb profile also gives 40GB, but only one fits per GPU and three compute slices are left unused. For 40GB workloads, the 3g.40gb profile is usually the better choice.

MIG mode also changes how the platform works in two key ways. First, all GPU Assignment Policy settings are ignored; the host assigns MIG instances based only on availability, without using Best Performance or Consolidation logic. Second, GPUs in MIG mode cannot be used in full-GPU or multi-GPU setups which require time-slice mode. On Hopper-generation GPUs, dynamic MIG switching lets an idle GPU switch modes automatically, but this only happens when the GPU is completely empty. In a busy cluster, you need to plan for this when designing capacity.

## What Comes Next

These three modes affect not only how a GPU handles today's workload, but also how the host fits into the cluster's capacity over time. The next article will help you decide which mode, policy, and combination best fit your environment, and will look at what is possible when GPU isolation means you no longer need to separate production and testing workloads.
