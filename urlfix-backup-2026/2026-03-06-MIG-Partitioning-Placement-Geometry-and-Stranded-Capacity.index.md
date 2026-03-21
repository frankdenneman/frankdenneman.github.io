---
title: "MIG Partitioning, Placement Geometry, and Stranded Capacity"
linkTitle: "Part 8 - MIG Partitioning, Placement Geometry, and Stranded Capacity"
description: "A deep dive into MIG partitioning, placement geometry, and stranded capacity in GPU infrastructure for AI workloads."
date: 2026-03-06
url: "/posts/2026-03-06-MIG-Mode"
series: ["Architecting AI Infrastructure"]
series_order: 8
concepts: ["MIG Partitioning", "Placement Geometry", "Stranded Capacity", "GPU Placement"]
categories: ["ai"]
track: "AI Infrastructure"
---
## Architecting AI Infrastructure — Part 8

Previous articles in this series explained how time-sliced GPU sharing works
in both same-size and mixed-size environments. They showed
that choices like profiles and the order in which workloads start can directly affect GPU utilization and whether workloads are placed successfully. In this part, we look at MIG and the design choices that affect placement success and overall
resource utilization.

MIG takes a different approach to GPU sharing. Instead of multiplexing
compute resources between workloads, MIG splits the GPU into hardware instances. Each instance gets its own dedicated compute and memory slices
slices.

![MIG architecture](images/MIG-Architecture.svg)

Each instance offers three main features: fault isolation, individual scheduling, and a distinct address space.  When strict hardware isolation is required, MIG is the right solution because workloads cannot interfere with one another, and resource consumption becomes predictable.

Many admins and operators choose MIG as the technology to provide fractional GPUs without a strict requirement for hard isolation. This article focuses on that use case and identifies the challenges to successful placement and resource utilization, including how profile selection directly determines whether GPU capacity is fully consumed or permanently stranded."


## MIG Resource Model

Earlier articles in this series showed that GPU capacity is not determined solely by free memory. Capacity depends on how resources are divided and placed. MIG adds another layer of placement constraints.

All NVIDIA GPU architectures that support MIG, including Ampere, Hopper,
and Blackwell, have the same structure. Each GPU provides seven compute slices and eight memory slices. Profiles use both resources simultaneously, so each profile represents a specific combination of compute and memory slices that match the GPU's physical layout.

![MIG slices](images/MIG-slices.svg)

This article uses an H100 eighty-gigabyte GPU as an example. In this
setup, each memory slice represents ten gigabytes of framebuffer memory. Because compute slices and memory slices are allocated together,
free memory alone does not determine whether a new instance can start.
The required compute slices must also be available and match the correct memory region. The table lists the available MIG profiles for the H100-80GB GPU:

## H100 80GB MIG Profiles

| Profile | Compute slices | Memory slices | Memory |
|---|---|---|---|
| 1g.10gb | 1 | 1 | 10 GB |
| 1g.20gb | 1 | 2 | 20 GB |
| 2g.20gb | 2 | 2 | 20 GB |
| 3g.40gb | 3 | 4 | 40 GB |
| 4g.40gb | 4 | 4 | 40 GB |
| 7g.80gb | 7 | 8 | 80 GB |

These profiles show that MIG resource use is asymmetrical in most cases. Some profiles offer the same memory size but differ in compute capacity. For example, both 1g.20 GB and 2g.20gb provide 20 GB of memory but need different numbers of compute slices. 

![1g20-vs-2g20-profile](images/1g20-vs-2g20-profile.svg)

The same goes for the 40 GB profiles: 3g.40gb and 4g.40gb both use 40 GB of memory, but need different compute resources.

**This mismatch between compute and memory can lead to placement results that aren’t obvious at first.**

## Stranded Capacity

Because compute and memory slices don’t always match up, some GPU resources can go unused even when the device looks fully used. Take the smallest MIG profile, 1g.10gb. This profile consumes one compute slice and one memory slice. On an eighty-gigabyte GPU, seven instances can be created because the GPU exposes seven compute slices.

![1g10-on-H100](images/1g10-on-H100.svg)

The GPU still has eight memory slices. After placing seven instances, 10 gigabytes of memory remain unused, or to put it another way, stranded capacity. No compute slices remain, so no other instance can start. This behavior is easy to miss in MIG placement diagrams. These diagrams show memory placement regions, and seven 1g.10gb instances appear to fill the GPU completely. In reality, the limiting factor is compute slices, not memory.

![H100 MIG placement diagram](images/h100-profiles-v1.png)

## Placement Geometry

MIG profiles must align with specific memory placement regions inside the GPU. Profiles that consume multiple memory slices require a contiguous region.

The 3g.40gb profile consumes four memory slices. On an 80-gigabyte GPU, this creates two valid placement regions: memory slices 0--3 or 4--7.  [nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html) is NVIDIA's command-line tool installed with the driver. The mig -lgi flag lists all active MIG instances on the host — ***list GPU instances*** — including the profile each instance was created from and where it sits in the GPU's memory layout.
The output includes a placement column formatted as start:size, where start is the index of the first memory slice the instance occupies, and size is the number of slices it consumes. 

![nvdia-smi-mig-lgi-command-2x3g40](images/nvdia-smi-mig-lgi-command-2x3g40.png)

A 3g.40gb instance at 4:4 starts at memory slice 4 and occupies four slices, placing it in the second region. A 4g.40gb instance at 0:4 occupies the first region, the only region where its compute requirement can be met. However, as two 3g.40gb profiles are placed on the GPU, one compute instance is stranded.

![2x3g40-compute-instance-stranded](images/2x3g40-compute-instance-stranded.svg)

The important thing to note, and what the 40gb profiles show so well, is that MIG introduces two regions, one with four aligned compute and memory slices, and another with three. MIG placement rules require that compute and memory slices start at the same position, but they don’t have to end together.

A great example of this is the 4g.40gb profile. It will only be placed on memory slice 0, and thus directly aligns with compute slice 0. I got the luxury of having (temporarily) access to a Dell PowerEdge XE9680 HGX system, with eight H100 80 GB GPUs, seven empty. 


![Dell PowerEdge XE9680-nvidia-smi](images/Dell-PowerEdge-XE9680-nvidia-smi.png)

When I powered on seven VMs with a 4g.40gb profile, each VM was placed in the first placement region (0-4) of an H100 GPU. The last four memory slices of each GPU were still free, but those regions only have three compute slices, so you can’t place another 4g.40gb VM there.

![7-4g40gb-placement-order](images/7-4g40gb-placement-order.png)

However, you can power on VMs with a 3g.40gb vGPU profile. As shown in the screenshot, I started two VMs with that profile, and they were placed on GPU 1 and 2.

![3g40gb-and-4g40gb](images/3g40gb-and-4g40gb.png)

Keep in mind that existing instances are never rearranged. The way the GPU is set up determines what can start next. This means the order you start workloads matters, since it affects which profiles can still be deployed, even if there seems to be enough memory available.

## Placement Behavior

As described in <a href="{{< ref "posts/2026-02-17-how-vsphere-gpu-modes-and-assignment-policies-determine-host-level-placement/index.md" >}}">part 4</a>, vSphere doesn’t use host-level GPU placement policies when GPUs are in MIG mode. Placement follows the same approach used in mixed-size environments: it fills one GPU before moving to the next, while keeping as many placement options open as possible for future workloads. This behavior has improved a lot in the Hopper architecture, but Ampere sometimes has trouble placing larger profiles because it does not always consider future 4g40gb placements. ([Reddit](https://www.reddit.com/r/vmware/comments/1rejqhg/comment/o7fmst7/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)).

On hosts with more than one GPU, workloads are placed on one GPU until
that device can’t fit the requested profile anymore. The next workload is then placed on another GPU. The same idea applies inside the GPU: instances are placed to keep the largest possible contiguous regions, so larger profiles can still be deployed later.

A good example is the 3g.40gb profile. In my test cluster, I cleared out seven GPUs (except GPU 0, which was running a developer’s workload) and started five VMs, each with a 3g.40gb vGPU profile. As shown in the screenshot, the first VM was placed on GPU 0, placement id 4, leaving space for a future 4g.40gb profile. When the next VM was placed with a 3g.40gb profile, the vGPU manager selected GPU 1, leaving the other GPUs open for the possible placement of the largest profile, 7g.80gb. With each new placement, the vGPU manager puts the first vGPU profile on placement 4 before filling up the rest.

![multi-gpu-3g40gb-placement](images/multi-gpu-3g40gb-placement.png)

Please note that I registered all these VMs on this host to keep the test scope limited. In real-world scenarios, DRS, together with Assignable Hardware, distributes VMs across compatible ESXi hosts in the cluster based on cluster balance of CPU and memory and the availability of compatible GPUs.

## Profile Catalog Design

The asymmetric consumption of compute slices forces a deliberate choice when defining the profiles exposed through a self-service portal, because the profiles you include determine what users can request and how efficiently the GPU is used over time.

The 40-gigabyte profiles show this tradeoff clearly. A GPU can host two 3g.40gb instances, but only one 4g.40gb, because a second would need eight compute slices and the GPU only has seven. If you offer only 3g.40gb, one compute slice is always stranded on a fully loaded GPU. If you offer 4g.40gb along with smaller profiles, you avoid that waste but risk placement failures: the 4g.40gb profile can only be created in the first memory region, so if another instance is already there, placement is impossible no matter how much memory is left.

The 20-gigabyte profiles have the same issue in a different way. Four 2g.20gb instances can’t run on a single GPU—again, eight compute slices are needed, but only seven are available. If you include the 1g.20gb profile as an option, you can fit a fourth 20-gigabyte placement, but this makes stranded capacity more likely as the GPU fills with compute-light instances.

There is no configuration that eliminates this tension. Platform teams must decide whether to prioritize placement predictability by offering fewer profile options and more predictable behavior, or to offer the full range of profiles and accept that users may sometimes see failed placements or that some GPUs will have stranded capacity.

If you don’t need hard isolation, mixed mode described in <a href="{{< ref "posts/2026-02-24-mixed-size-vgpu-mode-in-practice/index.md" >}}">part 6</a> and <a href="{{< ref "posts/2026-03-01-same-size-vs-mixed-size-placement/index.md" >}}">part 7</a> avoids these constraints completely. Four 20-gigabyte workloads and two 40-gigabyte workloads can each fully use a GPU in mixed-size environments without leaving compute capacity stranded.

##Looking Ahead
The next part covvers the new VCF9 functionality called 'DirectPath Profiles' to monitor placed GPU workloads and provide visibility into available GPU resources.
