---
title: "Stranded Capacity"
description: "GPU resources that remain unused because placement constraints prevent additional workloads from being scheduled."
url: "/concepts/stranded-capacity/"
---

Stranded capacity refers to GPU resources that cannot be used even though they appear available.

This occurs when placement constraints prevent additional workloads from fitting into the remaining resource layout.

Examples include:

- MIG compute slices remaining without matching memory slices
- vGPU placement regions that no longer align with available profiles
- cluster-level fragmentation caused by workload order

Stranded capacity is a common outcome of fractional GPU sharing and is strongly influenced by placement geometry and profile selection.

Relevant articles:

- /posts/2026-03-06-MIG-Mode/
- /posts/2026-03-01-same-size-vs-mixed-size-placement/
