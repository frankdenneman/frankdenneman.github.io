---
title: "Durable Agentic AI Sessions in GPU Memory"
linkTitle: "Part 3 - Durable Agentic AI Sessions in GPU Memory"
description: "How agentic AI workloads accumulate KV cache across reasoning steps and tool calls and why this changes GPU memory planning for on-prem infrastructure."
date: 2026-03-12
url: "2026-03-12-durable-agentic-ai-sessions-in-gpu-memory"
series: ["Understanding AI Memory"]
series_order: 3
concepts: ["Durable Agents", "Prefill", "Tool Calling", "KV Cache", "LLM Runtime Memory", "Agentic AI"]
categories: ["ai"]
track: "AI Memory"
---

## The durable memory of agentic systems

When a user asks a question in a chat interface and the model responds, the interaction is a single prompt completion. A prompt goes in, tokens come out. From an infrastructure perspective this is a predictable transaction. As described in [The Dynamic World of LLM Runtime Memory]({{< ref "posts/2026-01-12-the-dynamic-world-of-llm-runtime-memory/index.md" >}}), the KV cache grows with the prompt, peaks during generation, and is released when the session ends. The memory footprint is bounded and relatively easy to plan for.

Agentic AI behaves differently. Instead of answering a single prompt, an agent executes a sequence of steps. It reasons about a goal, calls a tool, evaluates the result, and continues until the task is complete. Each step is technically another prompt completion, but the agent does not start fresh each time. It carries forward the entire history of the task, including every prior LLM completion, tool result, and reasoning step, all of which are sent back to the model on every next call.

From the perspective of GPU infrastructure, this changes the memory lifecycle of the workload.

Architecturally the system still appears stateless. Each request is processed independently and the LLM returns a response. What persists across steps is the accumulated textual context. Agents do not store session memory in GPU memory directly. They store it in the text history that is repeatedly sent back to the model. That history lives in the agent framework's process memory, container memory in most deployments. It is not persistent. A container restart means the session history is gone and the agent must start over, spending tokens and utilizing GPU memory all over again. For long-running agentic sessions this is not just inconvenient, it is costly. How to protect session state across failures, and where to durably store it without rebuilding from scratch, is a topic for a future article.

This difference matters for infrastructure operators. Prompt completion workloads have short and predictable memory lifecycles. Agentic workloads accumulate memory across the lifetime of a task. A GPU that comfortably runs many concurrent chat sessions may struggle with only a few active agents. The model has not changed. The memory lifecycle has.

## State, memory, and the cost of continuity

Every step of an agent session is processed during the prefill stage, where the full session transcript is converted into a KV cache before token generation begins. As the session grows, prefill becomes increasingly expensive, both in compute and in the GPU memory required to hold the resulting cache. This is often the first bottleneck when scaling agentic inference, because prefill cost scales with context length, not with the number of tokens being generated.

Some inference systems reduce this cost through KV persistence layers such as [LMCache](https://github.com/LMCache/LMCache) or [prefix caching in vLLM](https://docs.vllm.ai/en/stable/design/prefix_caching/), which reuse previously computed KV segments rather than rebuilding from scratch on every step. Without such mechanisms, every step pays the full prefill cost of the entire session history. That these tools exist at all signals that the industry recognizes GPU-bound KV cache as a structural bottleneck worth solving at the infrastructure layer.

Prefill and decode also have fundamentally different compute and memory characteristics, which is why disaggregated serving, where the two stages run on separate infrastructure and scale independently, is an increasingly common pattern in production deployments. That topic is covered in a future article in this series.

The KV cache of an active agent session is **durable**. It is neither short-lived like a single prompt completion nor permanently stored like database state. It exists for the lifetime of the task and grows as the session context expands. This introduces a useful distinction when thinking about runtime state.

| Model behavior | Description | Example |
|----------------|-------------|---------|
| Stateless | Each request is independent | Standard API call or prompt completion |
| Durable | Memory persists for the lifetime of a session | KV cache of an agent session |
| Stateful | Memory persists indefinitely across sessions | Database-backed application state |

For vSphere administrators, the closest parallel is a VM's memory swap file, present for the life of the VM, growing under pressure, reclaimed only when the VM powers off. The session is the VM. The KV cache is the working memory it consumes while running. For Kubernetes operators, think of an emptyDir volume, scoped to the pod lifecycle, gone when the pod terminates.

## KV cache memory and session concurrency

Agentic sessions do not grow at a fixed rate. Three distinct mechanisms drive context accumulation, and each compounds the others.

Tool outputs inject tokens directly into the session history with no summarization or filtering. When an agent calls an external system, a ServiceNow query, a RAG retrieval, a code execution result, the full response is appended verbatim before the next step begins. A query that returns 500 tokens one day may return 8,000 the next. No configuration parameter at the inference layer caps this. For a deeper look at how agents, tools, and MCP servers fit together, Sam McGeown's primer [Understanding Instructions, Context, Skills and MCP Servers](https://www.definit.co.uk/2026/03/understanding-instructions-context-skills-and-mcp-servers-for-code-generation/) is an excellent starting point.

Reasoning-capable models add a second source of growth that is invisible to standard monitoring. Before generating a response, these models produce an internal chain-of-thought trace, real tokens with real KV cache cost, that never appear in logs or user-facing output. A complex reasoning step can add several thousand tokens per iteration. Sizing based on observable token counts alone will systematically underestimate actual GPU memory consumption.

The accumulated history of all prior steps is the third. Every completion, tool result, and reasoning trace is carried forward in full. Together these mechanisms push active sessions toward contexts that are larger, less predictable, and longer-lived than anything a prompt-completion sizing model accounts for.

## Quantifying the problem

To make the memory impact concrete, consider a realistic enterprise workflow: an AI agent that analyzes GPU cluster utilization, evaluates upcoming project demand, checks budget constraints, and raises a ServiceNow change request for capacity expansion. Ten steps, three tool integrations, three reasoning phases.

Each step adds tokens to the session history and the KV cache grows with it. For GPT-oss 120B the cost is approximately 0.035 MB per token, derived from its hybrid attention architecture of 18 full-attention and 18 sliding-window layers. The full architectural breakdown is covered in [Part 2 of this series](https://frankdenneman.ai/posts/2026-02-05-understanding-activation-in-mixture-of-experts-models/).

{{< diagram src="/diagrams/diagram1.html" height="580" >}}

The chart shows three distinct growth patterns. Tool calls produce the steepest jumps, their size determined entirely by what the external system returns. Reasoning steps add substantial invisible overhead that never surfaces in logs. The session closes at 854 MB, but the more important infrastructure detail is duration. That 854 MB is held in GPU memory for the full lifetime of the task. Other agents running concurrently may carry heavier contexts or run longer. Each session is a different size, with a different lifetime, and none release memory until their task completes. Fitting an unpredictable mix of sessions into a fixed pool of GPU memory is less a capacity calculation and more a bin packing problem, and unlike compute scheduling, the bins do not empty on a predictable schedule.

## Designing for durable sessions

The bin packing problem has a hard constraint we have not named yet. The bins are not empty, roughly 60 GB of every H100 80GB is already occupied before a single agent session begins. That is the model weights, static, always resident, loaded once and never released, as described in Part 1 and Part 2 of this series. What remains is the headroom that all active sessions must share. Agentic workloads make that headroom increasingly contested, sessions are larger, they run longer, and the dynamic memory consumption compounds with every concurrent agent. There are two architectural responses, and they solve different problems.

Multi-GPU deployment splits a single model instance across multiple GPUs using tensor or pipeline parallelism. This addresses size, models too large to fit on a single GPU can be distributed across several. The memory pool grows, but it still serves one model instance. The bin packing problem remains, just with a larger bin.
Multi-replica deployment runs multiple complete model copies, each on its own GPU or set of GPUs. This addresses concurrency, each replica maintains its own independent session pool, and a fleet of replicas is capable of handling thousands of simultaneous agent sessions. Here the number of bins grows, not their size.

In practice, large-scale agentic deployments require both. A model that requires multiple GPUs to load is deployed with tensor parallelism to handle size, then replicated across multiple such instances to handle concurrency.

A long-standing concern with multi-replica deployments was naive load balancing, routing each request to the next available replica regardless of session history, landing on a cold KV cache every time. For stateful chat that was a real liability. For agentic AI it largely disappears. Because the full session transcript is sent with every request, any replica can reconstruct the KV cache from scratch. The property that makes agentic sessions expensive, carrying the full history, is also what makes them portable. Session affinity matters less when the session carries itself.
Designing for durable, long-running sessions across multiple GPUs and replicas is the infrastructure challenge that follows from everything covered in this article. That is where the next article in the [Architecting AI Infrastrucre](https://frankdenneman.ai/ai-infrastructure/) begins
