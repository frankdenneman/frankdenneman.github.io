---
title: "Why GPU Placement Becomes the Defining Problem"
date: 2026-02-09T09:00:00+01:00
draft: false
categories: ["ai"]
tags: ["GPU Placement", "AI Platform", "VMware Private AI Foundation", "Kubernetes", "vSphere", "Scheduling"]
slug: "why-gpu-placement-becomes-the-defining-problem"
---

## Architecting AI Infrastructure Series - Part 1"

In earlier articles, I looked at how modern AI models use GPU resources. I covered [dynamic memory consumption](https://frankdenneman.nl/posts/2026-01-12-the-dynamic-world-of-llm-runtime-memory/), activation patterns, and how designs like [mixture-of-experts](https://frankdenneman.nl/posts/2026-02-05-understanding-activation-in-mixture-of-experts-models/) change resource needs over time. Those pieces focused on what models require from accelerators. This new series shifts the focus. Instead of starting with the model, we will look at the platform itself.

The goal of *Architecting AI Infrastructure* is to understand what changes when AI workloads move from ad-hoc experiments to long-running production services. At this stage, models need to be deployed, scaled, upgraded, and retired in a predictable way. GPUs are no longer tied to a single project, but become shared resources that support many teams, models, and use cases over time.

This article sets the scene. It explains why GPU placement is challenging, why early AI platforms often struggle as they grow, and why solving placement issues requires a new way of thinking about architecture rather than just introducing another scheduler.

## From experiments to services

Early AI platforms usually grow in a natural, unplanned way. A team gets GPU servers, installs Kubernetes on them, and begins experimenting. They train, fine-tune, or deploy models for inference. At this point, keeping things simple is more important than being efficient. If a GPU is idle, no one worries too much.

This approach works well at first. Workloads are similar, usage patterns are easy to predict, and overall utilization is low. Direct hardware access feels efficient, and the trade-offs are manageable because the platform is small and changes do not happen often.

Things change when AI shifts from being a project to becoming a service. At this point, the platform needs to handle different types of models, each with its own resource needs. It must deliver predictable performance and adapt to constant change. GPUs are no longer just for experiments; they become shared infrastructure. When this happens, placement decisions start to have hidden impacts.

## The hidden cost of placement decisions

Every AI workload placed on a GPU makes a choice, often implicitly, about how that GPU can be used in the future. A placement decision may consume a specific amount of memory, lock a GPU into a particular partitioning mode, or occupy a topology boundary, which can impact future workload placement.

The key thing about these decisions is that they usually work at first. They seem fine in the moment, but they quietly limit future choices. Over time, these choices add up, and the platform ends up in a common situation: there looks like there is enough GPU capacity, but new workloads cannot be placed.

This is not mainly a problem of utilization. It is a problem of fragmentation. As time goes on, earlier placement choices reduce the number of ways the cluster can be used. GPUs are not fully used up, but they cannot be used for the new requests the platform needs to handle. So, capacity exists on paper, but not in reality.

## Why most schedulers struggle with GPUs

This issue is not limited to one platform or orchestration system. It happens because of how most schedulers are built.

Traditional schedulers work one request at a time. They check each workload separately, see if the needed resources are available, and place the workload if possible. After that, they move on to the next request.

This approach works well for resources like CPU and memory, which are easy to swap. It does not work as well for GPUs. GPUs have fixed memory sizes, specific hardware layouts, interconnect domains, partitioning modes, and rules about which workloads can run together. Treating GPUs as if they are all the same might let you place a workload today, but it can quietly remove options you will need later. The system ends up focusing on short-term wins instead of long-term stability.

## Signals from the ecosystem

As more organizations use GPUs at scale, the community has become more aware of these limits. In the Kubernetes ecosystem, projects such as [HAMI](https://project-hami.io/) and platforms like [Run:AI](https://github.com/NVIDIA/KAI-Scheduler) have emerged to introduce additional coordination, smarter scheduling, and a broader view of GPU usage beyond the placement of individual workloads.

The key point is not whether these methods improve utilization in certain cases, or which one is best. What matters is what their existence tells us. These methods exist because GPU placement cannot be solved just by looking at individual workloads. Any system that wants to use GPUs efficiently over time needs to see beyond the current request and understand constraints, compatibility, and future needs.

Put simply, GPU scheduling is not a pod-level problem. It is a platform-level problem.

## GPU placement is a lifecycle problem

This requires a new way of thinking. AI infrastructure is not just about placing one workload correctly. It is about placing many workloads over time and making sure the platform can handle future needs. Placement decisions should consider not only if a workload can run now, but also if running it a certain way will limit future options.

In practice, this means clearly separating what a workload wants from what is possible. Workloads state their needs, and the platform decides how and where to meet those needs without harming the long-term health of the system.

At this point, GPU placement is no longer just a scheduling feature. It becomes a core part of the platform’s architecture.

## Why virtualization changes the equation

Virtualization changes how placement decisions are made and reviewed. Instead of tying workloads directly to certain devices, the system keeps a global view of GPU resources, their compatibility, their layout, and how they are used now and in the future.

This approach lets the platform match what workloads want with what is possible, apply policies at different levels, and prevent fragmentation before users notice it. The benefit is not just abstraction, but careful control over how valuable and limited resources are used over time.

This is why virtualization becomes increasingly valuable as AI workloads move from experimentation to production. Not because it abstracts hardware away, but because it understands hardware deeply enough to manage it deliberately.

## What this series will cover
As this series continues, it will connect these architectural ideas to practical tools that vSphere administrators already know. We will look at how GPU usage models like passthrough, fractional vGPU, and multi-GPU setups affect placement; how host-level GPU policies and vGPU modes impact consolidation and fragmentation; and how cluster-level decisions are shaped by DRS, device groups, and hardware layout.

Building AI infrastructure means treating GPU placement as a core issue from the start. It is not something to adjust later, but something to plan for deliberately.

**Next in the series:** [GPU Consumption Models as the First Architectural Choice in Production AI](/posts/2026-02-11-gpu-consumption-models-as-the-first-architectural-choice-in-production-ai/)

