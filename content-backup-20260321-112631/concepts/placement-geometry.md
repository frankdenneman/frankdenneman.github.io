---
title: "Placement Geometry"
description: "How GPU partitioning models determine where workloads can be placed and how placement constraints influence deployable capacity."
url: "/concepts/placement-geometry/"
---

Placement geometry describes how GPU resources are divided into placement regions and how those regions determine where workloads can be scheduled.

When GPUs are partitioned using mechanisms like vGPU profiles or MIG instances, workloads cannot be placed arbitrarily. They must align with predefined memory and compute regions.

This means that even when free resources appear available, workloads may fail to start if the remaining capacity does not match a valid placement region.

Relevant articles:

- /posts/2026-03-06-MIG-Mode/
- /posts/2026-03-01-same-size-vs-mixed-size-placement/
- /posts/2026-02-24-mixed-size-vgpu-mode-in-practice/
