---
title: "GPU Consumption Models as the First Architectural Choice in Production AI"
date: 2026-02-11T09:00:00+01:00
draft: false
categories: ["ai"]
tags: ["GPU Placement", "AI Platform", "VMware Private AI Foundation", "Kubernetes", "vSphere", "Scheduling"]
---

## Architecting AI Infrastructure - Part 2

The [previous article](https://frankdenneman.nl/posts/why-gpu-placement-becomes-the-defining-problem/) covered GPU placement as part of the platform’s lifecycle, not just a scheduling step. These choices affect what the platform can handle as workloads evolve. Before making placement decisions, it’s worth asking: how do AI workloads use GPUs?

This question is important because not every GPU workload requires the same resources. Two services might both need accelerators, but can be very different in memory use, how they run, and how much they depend on other GPUs. These differences set the platform’s limits well before the scheduler gets involved. So, GPU consumption models are not just an optimization detail. They are the first architectural choice for any AI platform.

---

## GPU consumption follows request patterns, not scarcity

In most cases, users ask for the biggest configuration they can get. More GPU memory, more compute, and exclusive access are seen as the safest ways to ensure stable and consistent performance.

This behavior follows old patterns in how people use infrastructure. When performance is important, asking for more resources seems like the easiest way to lower risk. Bigger allocations are thought to prevent interference, make troubleshooting easier, and reduce uncertainty. What has changed is not user behavior, but the nature of GPU contention.

---

## Why GPU contention is different from CPU and memory contention

CPU and system memory have been built to handle oversubscription for a long time. Advanced schedulers, preemption, and memory management help manage contention smoothly. When CPUs are overloaded, workloads just slow down. When memory is tight, systems use reservations, limits, and reclamation to stay stable. GPU contention is different.

Depending on the setup, a GPU either shares execution over time or splits it into separate parts. In time-sliced setups, compute tasks are shared, but each workload keeps its own memory. A virtual GPU keeps its full frame buffer whether it’s busy or not. In partitioned setups like Multi-Instance GPU, the device is split into hardware-isolated units, each with its own compute and memory. So, sharing a GPU isn’t like traditional oversubscription. It’s more like structured isolation, with clear resource boundaries. This difference changes how we should think about GPU sharing.

---

## Fractional GPUs are not a compromise

People often describe fractional GPU use as a way to increase density or save costs. In reality, it matches the needs of many production AI workloads. Embedding models, rerankers, and inference services usually have small, fixed memory needs and focus on throughput. They need reliable access to acceleration, not full control of a device. What’s important is memory isolation and controlled compute access, not owning all the resources.

Modern quantization techniques support this change. Large models in formats like FP4 use much less static memory. Even models with tens or hundreds of billions of parameters might not fill a high-end accelerator’s memory. While dynamic memory use still matters, especially with many users, a static footprint alone doesn’t justify exclusive allocation anymore.

Here, fractional GPUs aren’t about oversubscription. They set realistic resource limits that match how workloads actually behave once we understand them. By clearly limiting GPU memory and compute, fractional GPUs define a workload shape the platform can manage reliably.

This model works best when both static needs and dynamic behavior are predictable. If memory use, concurrency, and execution patterns are well understood, you can set clear limits. Then, multiple workloads can run together without interference, and placement stays flexible. Stability and consistency come from clear, enforceable resource boundaries, not exclusivity.

---

## Passthrough and exclusivity

Passthrough remains an important consumption model in production environments that require predictability, consistent performance, and clear ownership of accelerator resources. When a GPU is set up for passthrough, it is consumed as a whole device. Assigning that GPU to a single workload removes contention and makes performance easier to measure. At runtime, the workload has full control over the device, with no interference from other users.

The key feature of passthrough is not how it works at runtime, but where rigidity is introduced. Enabling passthrough sets up the GPU to be used only as a full device. This is true whether or not the GPU is currently assigned to a virtual machine. When a virtual machine uses a passthrough GPU, the workload keeps this fixed consumption shape for as long as it runs.

Changing that shape is not something you can do at the workload level. It requires stopping the workload and reconfiguring how the GPU is set up and assigned at the host and device levels. Unlike vGPU-based consumption, where an administrator can pick a different profile or VM class and just reboot the virtual machine.

![](images/changing_workshape_passthrough_vs_GPU.svg)

This difference matters in environments where AI workloads change quickly. Data scientists often try new model versions, use new quantization techniques, and adjust serving parameters, all of which can change a workload’s resource profile. Hardware-level allocation assumes the right consumption shape is known ahead of time. When that is not true, the cost of rigidity becomes clear.

Tools like Dynamic DirectPath I/O can make placement more flexible and help with failure recovery by hiding the physical device identity at power-on. However, they do not change the main feature of passthrough: while the workload is running, the GPU stays a single, indivisible allocation unit.

Passthrough is not the wrong choice. It is the right option when workload requirements are stable and well understood. In environments with frequent change, it becomes a deliberate architectural decision that trades adaptability for certainty.

---

## Full GPUs as a necessity, not a preference

Assigning a full GPU to a workload is often not about comfort or simplicity. In many cases, it is a direct result of the workload’s resource needs.

Some workloads require the full capacity of a GPU to run properly. Their static memory footprint may already use most of the device, leaving little room for sharing. Others have dynamic behavior where memory use grows with sequence length, batch size, or concurrency, making it hard to set safe fractional boundaries.

User behavior shows this pattern. When data scientists are sure a workload fits within clear memory and compute limits, they often use fractional GPUs. When they are not confident, they tend to use full GPUs to regain predictability.

Full GPUs are often chosen because the workload shape is uncertain, not because sharing is undesirable. In many cases, the static requirements of a model are well understood and clearly fit within GPU memory. What remains unknown is how the application will behave under real traffic. Consumption rate, concurrency, input variability, and batching strategies all influence dynamic memory usage, and these characteristics are often only discovered after deployment. Allocating a full GPU becomes a way to absorb that uncertainty while the workload’s true behavior reveals itself.

It is important to distinguish this consumption model from passthrough. A full GPU may be delivered through passthrough or through a full-size virtual GPU profile. In both cases, the workload consumes the entire device. What differs is how the platform manages placement and lifecycle. What remains consistent is that the unit of allocation is the full GPU.

From a platform perspective, full-GPU consumption introduces stronger constraints than fractional sharing. Each placement fixes the workload shape at the largest possible granularity. This does not make full GPUs inefficient or undesirable. It makes them precise. They are the correct choice when the workload requires it.

---

## When a workload spans GPUs

When a workload needs more than one GPU, GPU consumption changes in a fundamental way. The GPU is no longer the unit of placement. Multi-GPU workloads are not just larger versions of single-GPU workloads. They depend on communication between devices, often at bandwidths higher than what PCIe alone can provide. At that point, topology becomes part of the contract between the workload and the platform.

Distributed model serving, large-scale inference, and training workloads rely on fast interconnects to synchronize parameters, exchange activations, or shard model state. Technologies such as NVIDIA [NVLink and NVSwitch](https://www.nvidia.com/en-us/data-center/nvlink/) enable this communication at scale.

From a placement perspective, this creates a hard boundary. GPUs can no longer be treated as independent units. They must be allocated as connected groups, and the topology of those connections directly affects which hosts can satisfy the request and which future placements are possible.

---

## GPUs are not isolated from the system

GPU consumption never exists in isolation. Every GPU-accelerated workload depends on system memory and CPU resources to feed data, manage execution, and handle results. The way a workload consumes GPU resources directly shapes what it requires from the rest of the system.

Static GPU memory footprint sets a baseline requirement. Model parameters must stay in GPU memory at all times, no matter the workload activity. Dynamic behavior, such as activations and key-value caches, determines how the workload scales with concurrency. These GPU characteristics do not exist in isolation. They directly dictate how the workload must be provisioned at the system level.

The amount of GPU memory consumed and how it is accessed determine how much CPU is needed to feed the device, how much system memory must be reserved to support the working set, and how closely the virtual machine must align with [NUMA](https://frankdenneman.nl/categories/numa/) boundaries. In other words, choosing a GPU consumption model also defines the CPU and memory shape of the virtual machine that can support it.

Once that VM configuration is set, placement decisions go beyond the GPU. Host selection, CPU scheduling flexibility, memory locality, and even cluster-level behaviors like vSphere HA admission control are all affected by what first seems like a GPU-only choice.

---

## Consumption models shape everything that follows

Traditionally, GPU allocation was handled near the infrastructure layer. Now, that decision is happening at higher levels. New Kubernetes features, such as 

[Dynamic Resource Allocation (DRA)]: https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/

, let workloads specify their hardware needs directly in their scheduling requirements.

With DRA, workloads can now make structured ResourceClaims, which drivers use to pick compatible devices. While the full range of features is still developing, the main trend is clear: allocation decisions are becoming more declarative and focused on workload needs.

In the future, this approach could let workloads set ordered hardware preferences (cascading ordered GPU list). Instead of just asking for one device, a workload could list preferred GPU types, memory sizes, or features. This way, a pod could share a flexible wish list, and the scheduler and driver would pick the best available device at runtime.

Even as these abstractions mature, one principle remains constant. A GPU, once allocated, is still consumed as a discrete unit. What changes is not the granularity of the device itself, but the layer at which intent is declared, and binding happens. Within that limit, different GPU consumption models create different constraints for the platform.

Each GPU consumption model brings different constraints to the platform. Passthrough favors predictable performance. Fractional GPUs keep flexibility once behavior is understood. Full GPUs absorb uncertainty. Multi-GPU workloads make topology a first-class requirement, pulling in more system resources for placement decisions.

The architectural challenge is not picking a single GPU consumption model, but making sure different workload needs can be met at the same time. Workloads express their needs through different consumption models, while the platform enforces isolation, makes correct placement decisions, and keeps global awareness across hosts and clusters. Solving this challenge lets GPU resources be used efficiently over time without fragmenting the platform.

---

## Looking ahead

The next articles in this series will move from consumption models to placement mechanics. It covers how host-level GPU policies, CPU and memory reservations, and cluster-level behavior interact with the workload shapes described here.
