---
title: "The Agent Sends Everything, Every Time"
linkTitle: "Part 4 - The Agent Sends Everything, Every Time"
description: "An agent resends its entire context with every model call: in one Codex session, 1.4M input tokens to deliver 84K of new information. This article explains why that repetition makes the KV cache the deciding factor in GPU compute per request, how LRU eviction works like a conveyor belt, and why cache misses cause more cache misses under load."
date: 2026-10-22T12:00:00+02:00
url: "/2026-10-22-the-agent-sends-everything-every-time/"
series: ["Agentic Workloads"]
series_order: 4
concepts: ["AI Agents", "KV Cache", "Prefix Caching", "Prefill", "Cache Eviction", "LRU", "Inference Efficiency", "vLLM"]
categories: ["ai"]
track: "Agentic Workloads"
aliases:
  - "/posts/2026-10-22-the-agent-sends-everything-every-time"
  - "/2026-10-22-The-Agent-Sends-Everything-Every-Time/"
  - "/2026-10-22-the-Agent-Sends-Everything-Every-Time/"
  - "/2026/10/22/the-agent-sends-everything-every-time/"
---

## The model remembers nothing, the server might

The [previous article](https://frankdenneman.ai/2026-10-22-anatomy-of-an-agent-request/) examined how an agent builds an inference request and how its context grows as the task progresses. But why does the agent need to send so much information with every request? The answer starts with a fundamental characteristic of how language models operate: the model itself does not remember previous requests.

Every inference request is a new execution, and the model can only reason about information included in its current input.

During inference, input tokens pass through the model's layers, producing intermediate values called activations. These activations are temporary, and their memory can be reused once they are no longer needed. The model's weights remain unchanged, so after the request completes, the model itself returns to the same baseline it had before the request.

For an agent, the full context provides continuity. The system instructions define how the model should behave. Tool definitions describe which actions are available. The conversation history contains the original task, decisions already made, actions taken, and results returned by tools. Without that information, the model could repeat work, contradict earlier decisions, or lose track of the task it is trying to complete.

The agent harness maintains this context and sends it with each new inference request. The inference engine may still hold the KV cache from an earlier request, allowing it to reuse previously computed attention states. However, that cache is managed by the inference engine, not the model or agent harness, and may be evicted when memory is needed.

This explains why the final request in the Codex session from the previous article contains 83.4K input tokens, even though only 1.6K tokens represent new information. The agent harness sends the accumulated context to preserve continuity, while the inference engine determines how much of the previous computation it can reuse.

This repeated context has significant consequences for inference infrastructure. Processing the same tokens again consumes GPU compute, increases request latency, and reduces the capacity available for other workloads. Reusing previously computed KV cache entries can avoid much of that work, but only if the cache is still available when the next request arrives.

This article examines what happens to those repeated tokens, the computational cost of processing them again, how prefix caching reduces that cost, and why the time between agent requests matters for cache retention and overall GPU efficiency.

## The agentic payload

![Anatomy of one agentic trace, from the vLLM x Mooncake analysis. Each row is one model call; striped segments were sent before, orange is new.](images/anatomy-of-an-agentic-trace.png)

The figure comes from the vLLM team's analysis of 610 Codex sessions on SWE-bench Pro, the same [vLLM x Mooncake](https://vllm.ai/blog/2026-05-06-mooncake-store) study the previous article drew its per-turn medians from. Read it row by row and the pattern is plain. Every request starts with the same 11.5K tokens: system prompt, tool definitions, skills. Then comes everything the session has produced so far. Only the orange segment at the end is new: 6.2K of file contents on turn 1, 5.8K of grep results on turn 2, 1.6K of command output on the final turn.

Add up the whole session. Thirty requests grow from 12K to 83.4K tokens, so the harness sends roughly 1.4M input tokens over the run. The new information in all of them together is about 84K tokens, the size of the final context. About 94% of every token the endpoint receives is a token it has received before.

| Segment | Tokens per request | Sent over 30 requests |
| --- | --- | --- |
| Static prefix (system prompt, tools, skills) | 11.5K | ~345K |
| Session history (task, past decodes, past tool output) | 0 → 70K | ~1.0M |
| New tool output | 1.6K–6.2K | ~72K |
| Output (decode) | 250–640 | ~9K |

The middle column is one request; the last is the sum over all thirty, because every segment is resent each time. The history grows from 0 to 70K, so it averages about 35K per request and adds up to about 1.0M.

The output column explains why agents are called input-heavy: about 150 input tokens per output token. The first two columns explain why that ratio is misleading. Almost none of that input is new; the question is whether the GPU processes it as if it were.

*Totals assume the context grows evenly between the published turns; they are approximations, not measurements.*

## What a cache hit saves the session

A cache hit turns an 83.4K-token prefill into a 1.6K-token prefill. Before the model produces its first output token, it runs every input token through every layer and stores each token's keys and values: the KV cache. That prefill is the compute-bound, expensive phase of a request. If the KV cache from the previous turn is still in GPU memory, the server skips those tokens and computes only the new ones.

Across the session the difference is roughly 17x in prefilled tokens: about 84K with every turn hitting the cache, about 1.4M with every turn missing. For a dense 70B-parameter model at roughly 140 GFLOP per token, that is around 12 PFLOP versus 200 PFLOP for the same work and the same answer. The FLOPs a hit saves do not disappear; they are available for other sessions on that GPU.

The saving is smaller than the token count suggests, and it is worth saying why. The new tokens still attend to the whole cached context: each of the 1.6K new tokens is compared against all 83K cached keys, and the GPU reads those cached keys and values from memory to do it. A hit removes the computation for the old tokens, not their memory footprint. A cache hit also reduces time to first token and end-to-end latency. On a hit, only the 1.6K new tokens need to be computed; on a miss, all 83.4K. Waiting on that computation adds to the session's loop latency on every model call that misses the cache.

## What a cache hit saves everyone else

A cache hit does not only make one session cheaper; it returns GPU time to every request sharing that GPU. Three effects add up.

**The static prefix is shared.** The first 11.5K tokens are identical for every session of the same agent. An inference server such as vLLM stores the KV cache in fixed-size blocks and identifies each block by a hash of its tokens and of every token before it. Two sessions with the same opening tokens map to the same blocks, so one copy in GPU memory serves a hundred sessions. This is also why the harness puts the unchanging parts first: a block is reusable only if everything in front of it matches, so one changed token early in the request, a timestamp in the system prompt for example, makes everything after it unique.

**Prefill competes with decode.** Most model deployments batch prefill and decode work together, and a long prefill takes its share of each step's compute budget for many steps in a row. A session that misses and recomputes 80K tokens slows the token generation of every other request on that GPU while it does. A cache hit avoids that slowdown entirely.

**Cached blocks hold no memory back from running requests.** A cached block that no running request uses is not reserved. It sits in the free block queue, available for reuse if its prefix comes back, overwritten if the server needs the space. Caching is opportunistic: it fills memory that would otherwise be empty, and gives it up the moment active requests need it. That is the mechanism the next section is about, because it decides how long a session's history survives.

## The cache is a conveyor belt

At startup, vLLM reserves the GPU memory left over after the model weights for the KV cache and divides it into fixed-size blocks, the block pool. A block in the pool is either in use or free. In-use blocks belong to running requests, in prefill or decode, and cannot be evicted. Free blocks belong to finished requests and sit in the free block queue: their contents stay in GPU memory and can be reused, until vLLM needs the space for another request.

A useful analogy for that queue is a conveyor belt with a drop at the end. When the request ends and the agent goes back to waiting on a tool, its blocks change from in use to free and go on the belt. vLLM evicts with a least-recently-used (LRU) policy: whenever the inference engine needs a block for any request, it takes the free block that has gone unused longest, the one at the drop, and overwrites it. Every other free block moves one step closer to the edge. If the session's next request arrives while its blocks are still on the belt, the inference engine finds them, marks them in use again, and skips computing them. The [vLLM prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/) describes the free block queue and its LRU eviction in detail.

<iframe src="/animations/kv-cache-conveyor-final.html?embed" title="The KV cache is a conveyor belt" loading="lazy" style="width:100%;height:760px;border:0"></iframe>

The animation follows one session through three tool cycles. Each request adds a block: last turn's new tool output, orange, turns blue as the GPU pulls it back in, because it is now part of the prefix. Try the three tool waits. At the 5.2-second median, the prefix is still on the belt every time and the GPU prefills only the new tool output. At 20 seconds on a busy GPU, the newest blocks fall off first and the GPU recomputes them. At the 81-second P99, the whole prefix is gone, and the GPU spends visible time computing it again before it can start on the new work.

The belt explains which parts of the trace survive a tool wait:

- **The prefix grows every turn, and so does what is at risk.** After thirty turns the session has 80K tokens on the belt, all of them already prefilled once.
- **Eviction takes the tail first.** vLLM returns a finished request's blocks in reverse order, so the newest blocks of a sequence reach the drop before its oldest. The reason, per the [vLLM design](https://docs.vllm.ai/en/latest/design/prefix_caching/): a request's last block hashes the most tokens, so it is the least likely to be reused by another request, and should be evicted first. A partially evicted session keeps the start of its prefix and recomputes its most recent turns, rather than losing everything.
- **The shared part of the prefix rarely reaches the drop.** The system prompt, tool definitions and skills are identical across all sessions of the same agent, such as the 610 Codex sessions in the trace data. Other sessions of that agent on the same replica keep pulling those blocks back in. A different agent shares none of them: its system prompt differs, so its very first block already hashes differently. The animation leaves this out for clarity; a session's own history only gets pulled back by that session.

The belt's speed is not set by the session. It is set by everything else on the GPU: other agent sessions, chat traffic, a batch job, a RAG request with a large document. The time a block survives is roughly the free cache capacity divided by the rate at which new tokens arrive. An illustrative case: 500K tokens of free cache (about 160 GB of KV cache at roughly 320 KB per token, for a 70B-class model with grouped-query attention at BF16, spread across a node) and 100 sessions like the Codex one, each adding about 3K tokens every 10 seconds. That is about 30K tokens per second, and a belt about 17 seconds long. A 5.2-second tool wait comes back well before the drop; an 81-second wait comes back to an empty belt.

Cache misses make the belt faster. The belt moves one step for every block the inference engine allocates. A request that hits allocates blocks only for its new tokens, 1.6K tokens' worth. A request that misses allocates blocks for its entire context again, 83.4K tokens' worth: in the example above, about a sixth of the belt in a single request. Every free block moves that far toward the drop at once, so other sessions' prefixes are evicted sooner, their next requests miss, and their recomputes push the belt further still. The recompute also holds the request on the GPU longer, so the agent's loop slows down too. Under load, misses cause misses.

## Closing: the wait decides the hit

The belt turns a question about GPU memory into a question about time. Whether a session's next request hits the cache depends on how long its blocks sit on the belt, and that time is the tool wait. The tool wait is not set by the GPU. Part of it is the task itself: running a full test suite takes longer than reading a file, however fast the platform is. The rest is set by storage I/O, by CPU headroom, and by how quickly a sandbox can start or resume: the platform underneath the agent, and the part a platform team controls.

The next article, *Sandbox Performance Decides the KV Cache Hit*, looks at that platform: which tools need a sandbox, where sandbox startup lands in a session's lifecycle, and why warm pools, resumes and snapshots are inference capacity decisions, not just agent infrastructure.
