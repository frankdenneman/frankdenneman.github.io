---
title: "NUMA Locality"
description: "The relationship between CPU sockets, memory, and devices such as GPUs in multi-socket systems."
url: "/concepts/numa-locality/"
---

NUMA locality describes how processors, memory, and devices are physically connected inside multi-socket systems.

In NUMA systems, each CPU socket has local memory and attached devices. Accessing local resources is significantly faster than accessing resources connected to another socket.

For GPU workloads, maintaining NUMA locality can improve performance by reducing cross-socket memory traffic and latency.

Relevant articles:

- /posts/2016-07-07-numa-deep-dive-part-1-uma-numa/
- /posts/2020-01-30-machine-learning-workload-and-gpgpu-numa-node-locality/
