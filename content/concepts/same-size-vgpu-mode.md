---
title: "Same-size vGPU Mode"
description: "A vGPU configuration where all workloads on a GPU must use the same profile size."
url: "/concepts/same-size-vgpu-mode/"
---

Same-size vGPU mode requires all virtual machines sharing a GPU to use the same vGPU profile size.

Once the first workload is placed, the GPU becomes locked to that profile size. All subsequent workloads must use the same profile.

This simplifies placement decisions but can reduce flexibility and lead to unused capacity if workloads request different profile sizes.

Relevant articles:

- /posts/2026-02-19-how-same-size-vgpu-mode-and-right-sizing-shape-gpu-placement-efficiency/
- /posts/2026-03-01-same-size-vs-mixed-size-placement/
