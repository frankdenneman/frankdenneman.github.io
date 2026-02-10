+++
date = '2026-02-04T23:03:39+01:00'
title = 'Understanding Activation Memory in Mixture of Experts Models'
categories = ['ai']
+++ 

In my previous article, [The Dynamic World of LLM Runtime Memory](https://frankdenneman.nl/posts/2026-01-12-the-dynamic-world-of-llm-runtime-memory/), I focused on KV-cache as the primary driver of runtime memory pressure. Today, as inference workloads move toward long-context and agentic execution, activation memory has emerged as an equally important and often overlooked constraint.

Long-context inference, once niche, is now expected as models handle tens of thousands of tokens in lengthy prefill phases. Agentic inference introduces variable execution, including reasoning, tool calls, pauses, and uneven token generation. These patterns put sustained pressure on both KV-cache and intermediate activations.

This article moves the focus from the KV cache to the activation memory. Before diving into its behavior in Mixture of Experts (MoE) models, which route inputs through specialized experts, it’s important to examine the evolving phases of inference that highlight the importance of activation memory.

### Prefill versus decode

To see why activation memory matters more now, it’s useful to look at how inference has changed.

Inference has two main phases. The prefill phase processes the entire input: prompts, history, documents, tool outputs, and any prior reasoning. The model runs a full forward pass over the complete sequence here. All layers are active, activations are created for every token, and KV cache entries are built but not yet reused.

The decode phase follows, generating tokens one by one while reusing KV cache entries. Activations are short-lived, so memory consumption stays steady and grows slowly.

Recently, decode-dominated workloads prevailed: prompts were short, prefill was brief, and memory pressure increased mainly with response length. Under these conditions, KV cache dominates memory use while activation memory remains mostly transient and remains unnoticed operationally.

Today, long context inputs cause models to process extended sequences in single prefill passes before producing output. In these, all layers are active across the sequence. Activation memory grows with context length, leading to peak memory use before the first output.

Agentic workflows amplify this pattern. Each pause, new context injection, or execution resume can trigger another prefill phase, making activation-heavy execution a recurring, not just initial, memory cost.

### Mixture of Experts

In dense language models like Llama 3.1, each transformer layer has a single feed-forward network. Every token passes through it, with weights used each time. As computation moves through the layer, intermediate, short-lived activations are stored until layer completion, contributing to runtime memory consumption. MoE  models replace each feed-forward network within each layer with multiple independent experts. 

Please note that experts increase model capacity without requiring all parameters for every token. Dense models use one feed-forward network for all patterns, while MoE  distributes capacity via routing across multiple experts per token.

Think of the model as a building: each layer is a floor, and every floor contains a room of specialists. In [gpt-oss-120b](https://arxiv.org/pdf/2508.10925), each room holds 128 experts. As a token moves through the model, it must pass through every floor in order. At each floor, it enters the expert room and is routed to a small number of specialists. In gpt-oss-120b, four experts are selected per token at every MoE layer. Those four experts together perform the feed-forward computation for that layer before the token continues upward to the next floor.

Unlike human education, there is no predefined meaning assigned to an expert. Specialization emerges during training. If an expert happens to perform slightly better on a certain class of tokens early on, the routing mechanism will tend to send more similar tokens to that expert. Over time, this creates a feedback loop in which different experts become optimized for different patterns in the data.

From a memory perspective, when an expert is selected, all its weights in the layer are involved in computation, creating intermediate activations that must remain in memory until the layer completes. Because multiple experts are selected per token, each one contributes its own set of activations. The cumulative effect of having several experts active per token increases the total activation memory footprint in each layer.

During long prefill phases, many tokens are processed simultaneously, each passing through all layers while multiple experts may execute in parallel. Activation memory thus grows with the number of tokens, layers, and experts per token, making MoE models show less predictable activation memory behavior than dense models.

### Quantifying the active payload per layer

A common assumption is that MoE models must be heavier at runtime because multiple experts execute per token. When measured at the single-layer level, that assumption does not always hold. The table below compares the number of parameters that actively participate in computation for a single token in a single layer.

| Model                               | LLaMA 3.1 70B (Dense) | gpt-oss-120b (MoE) |
| ----------------------------------- | --------------------- | ------------------ |
| Model Type                          | Dense                 | Mixture of Expert  |
| Feed-forward structure per layer    | 1 dense FFN           | 4 selected experts |
| Active parameters per layer         | ~882 million          | ~141 million       |
| Activation precision                | FP16 / BF16           | FP16 / BF16        |
| Approx. activation memory per layer | ~1.7 GB               | ~280 MB            |

### How these numbers were derived?

LLaMA 3.1 70B uses ~882M active parameters per layer, generating ~1.76 GB of activation data (at 2 bytes/param). 

gpt-oss-120b activates 4 experts totaling ~141M params per layer generating ~282 MB of activations. Each expert is far smaller than Llama's dense FFN; even combined, MoE uses ~6x less memory per layer despite selecting multiple experts per token.

These figures capture the dominant feed-forward activation costs (held until layer completion), excluding KV-cache or other buffers, highlighting MoE's clear inference memory edge.

### Why does MoE still stress activation memory?

Dense models generate a single large activation set per token per layer, predictable and concentrated, which GPUs handle efficiently with minimal allocation overhead and smooth memory usage.

MoE models create multiple smaller sets per token per layer, triggered conditionally by routing decisions that vary across tokens and layers.

During long prefill phases (when processing many tokens simultaneously), each token hits every layer with parallel expert activations. For an 8-token batch, this means 32 tiny memory allocations (4 experts × 8 tokens) versus dense's clean 8 chunks, thrashing the memory allocator, creating external fragmentation and peak spikes, even though total bytes (~2.25GB) are lower than dense (~7GB). Dense stays smooth; MoE gets jagged.

### The shift in failure mode

What ultimately changes with MoE models is not just how much memory is used, but *when* and *how* memory pressure appears.

In dense models, activation memory is dominated by a small number of computationally intensive operations. Memory usage rises and falls in a relatively smooth and predictable way, and failures tend to correlate clearly with context length or batch size.

In MoE models, activation memory is created in smaller pieces but repeated many times across tokens, layers, and routing decisions. Peak memory pressure emerges during prefill phases and can vary significantly depending on input composition and concurrency.

The result is a shift in failure mode. Dense models typically exhaust memory gradually and predictably. MoE models are more prone to sudden activation spikes that occur before the first token is generated, even when average memory usage appears safe, making it more difficult to monitor their resource consumption trends.

### The practical takeaway

MoE  models are not necessarily more computationally expensive than dense models, but they are more sensitive to context length, batching, and concurrency. Activation memory becomes harder to predict, even when the number of active parameters per layer is lower than in a dense model.

The key shift is that inference stability is no longer governed by steady-state behavior. It is governed by short-lived activation peaks during prefill and agent resumes. Infrastructure must therefore be sized and operated for these peaks, not for average utilization. This changes how hardware is selected, how workloads are placed, and how concurrency is controlled.

For on-prem enterprise platforms, this favors conservative, locality-focused designs during activation-heavy phases. Prefill and agent resumes create short, intense activation spikes that are both memory-bound and latency-sensitive. Keeping these phases within a single host or an NVLink or NVSwitch domain avoids network hops when memory pressure is highest. Expert routing is also frequent and fine-grained. Every layer and token involves routing decisions, and crossing hosts turns these into synchronization points, increasing tail latency and reducing operational stability.

This does not eliminate scale-out. Replication remains an effective way to increase capacity and isolation. However, distributing activation-heavy execution across hosts provides little benefit and increases fragility. For enterprise deployments, predictability matters more than peak throughput.

Shared environments require additional care. Dense models typically increase memory usage gradually, making overcommitment and time-slicing relatively safe when well tuned. MoE workloads exhibit sharper and less predictable activation spikes, especially during long prefill phases. This reduces the margin for error in multi-tenant deployments. GPU virtualization strategies must account for worst-case activation behavior, not just averages, and overcommitment techniques that work for dense models can lead to abrupt failures when applied to MoE workloads.

The core trade-off is simple. Dense models reward aggressive batching and tight packing. MoE and agentic models reward headroom, locality, and control. The infrastructure that succeeds in this next phase is not the one that maximizes average utilization, but the one that remains stable under bursty, activation-heavy execution.
