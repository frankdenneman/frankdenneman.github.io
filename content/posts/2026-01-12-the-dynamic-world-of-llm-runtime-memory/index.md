---
title: "The Dynamic World of LLM Runtime Memory"
date: 2026-01-12
categories: 
  - "ai"
---

When meeting with customers and architectural teams, we often perform a specific exercise to separate a model's static consumption (its weights) from its dynamic runtime consumption.

In the unpredictable world of production AI, where concurrent users, complex system prompts, and varying RAG content create constant flux, it is easy to view memory as an elusive target.

This article is designed to move your service level from probabilistic to deterministic concurrency. To make this accessible to those managing the hardware, I have intentionally used language common to system administrators rather than data scientists. Instead of focusing on the mathematical constructs of vectors and matrices, we will use the term representations to highlight the actual memory consumption of these data structures.

While these calculations are not a mandatory step for every deployment, they provide the essential north star for architects who are curious or need to establish a deterministic floor for their capacity planning.

**Dynamic Memory Consumption of User Prompts**

Or better said: KV cache memory calculation. Let’s use Llama 3.1 70B in FP16 with a maximum 32K token prompt as an example. How many bytes per token does it consume? The calculation is:

```
bytes/token = 2 (Key+Value) x Layers x kv_heads x head_dim x 2 (FP16 bytes) =
2 x 80 x 8 x 128 x 2 = 327,680 = 0.33MB / token x 131072 = 42.95GB *
```

_\* All memory sizes in this document are expressed in decimal gigabytes (GB), consistent with GPU vendor specifications._  
  
These specifications of the model can be found in its config.json file. Below is a screenshot of [Llama 3.1 70B config.json](https://huggingface.co/meta-llama/Llama-3.1-70B/blob/main/config.json):

![](images/llama-3.1-70b-config-json-632x1024.png)

Let’s look closely at each step of this calculation.

**2 (Key+Value)**

**What is stored per token?  
**For each token, the key and value vectors are stored in the KV cache.

**What is a key and value in the context of an LLM?**  
When a model reads a prompt, it needs a short-term working memory of the prompt and a mechanism to decide what parts of that memory matter for the next token. The [attention mechanism](https://arxiv.org/pdf/1706.03762) of the LLM answers the question:

_‘Given what I'm trying to generate now, which parts of the prompt should I look at, and how strongly should each of those tokens influence the answer?’_

The important thing to understand about attention\[b\]\[c\] is that it's about understanding the question and identifying relevant information from the LLM in the prompt to answer it. It’s not a database query looking for an answer in the model weights.

**Tokenization**  
As a result, the prompt's words are first tokenized. LLMs do not operate on words directly; they operate on tokens, which are then converted into numerical vectors. Tokens offer a finite, reusable set of symbols. Since not every possible word appears during training, the model must be able to compose meaning from smaller pieces. Common words are often represented as a single token, while rarer words may be split into multiple tokens. Tokens can represent whole words, parts of words, and punctuation. If we use the prompt ‘_What is the capital of Texas?_’ may be tokenized in the following way:

`[What] [is] [the] [capital] [of] [Texas] [?]`

**From tokens to token representations**  
At this point, the model is no longer operating on words, but on token representations (vectors). A token representation can be seen as a fixed-size data structure that summarizes a token’s meaning and role in the sentence. (For example, in a prompt about Apple it is distinguishing Apple the tech company from apple the fruit). Once the prompt has been tokenized and converted into token representations, the model begins processing the prompt step by step.

**Key and value information per token**

| Token | Key information | Value **information** |
| --- | --- | --- |
| \[What\] | Question indicator | Signals that an answer is required    |
| \[capital\] | Capital-city relationship | Information about capitals |
| \[Texas\] | U.S. state entity | Information about Texas |
| \[Is\] / \[the\] / \[of\] | Grammatical structure | Minimal semantic contribution |

As the model processes the prompt, attention is used to determine which tokens in the prompt are relevant to the current step, and how strongly each should influence the outcome.

**Queries, keys, and values in action**  
To do this, the model generates a query representation. The query does not describe the task in words; it is simply a signal that reflects what the model is currently working on.

Each token in the prompt has associated key information that describes what the token represents. The model uses the query to determine which tokens are relevant at the moment. Tokens that are more relevant have a stronger influence on the next step, while others contribute very little. In our prompt example, tokens such as \[Texas\] and \[capital\] are more relevant than grammatical tokens like \[is\], \[the\], or \[of\] because they carry the information needed to answer the question.

**Why do queries not appear in the memory calculation**?  
Although query representations play an important role in determining the relevance of each tokenin the prompt, they do not contribute to KV cache memory consumption. Query representations are generated on the fly, used once, and discarded immediately. From a system perspective, query representations reside only in temporary GPU memory, such as registers or short-lived activation buffers. Their memory footprint is small and short-lived, and does not grow with prompt length.\[f\]\[g\]

Keys and values, on the other hand, are generated once per token, must remain available for all future steps, and are therefore stored persistently in GPU memory as a part of KV Cache. This is why the memory calculation includes keys and values, but not queries.

**Layers, KV heads, and Grouped-Query Attention**  
So far, we’ve explained why keys and values dominate memory. The next question is: how many keys and values do we store per token? That is where layers, KV heads, and Grouped-Query Attention come in

**Layers multiple memory consumption**  
A transformer model is built from many stacked layers. Each layer performs its own attention operation, so each layer needs its own key and value for every token. This means that KV cache memory scales linearly with the number of layers. For example, in LLama 3.1 70B, the architecture has 80 layers, so each token stores 80 key-value pairs.

**How many Key/value pairs per layer?**  
Within each layer, attention is divided into multiple heads. Each head represents a separate way of interpreting the token information. Keys and values are stored per head, so the KV cache memory also scales with the number of KV heads.

**Grouped-Query Attention**  
In traditional multi-head attention, every query head has its own key and value head. Llama 3.1 uses Grouped-Query Attention (GQA), where many query heads share a smaller number of key and value heads. Llama 3.1 70B has 64 query heads, but only 8 KV heads. This reduces the KV cache memory by a factor of 8x compared to traditional multi-head attention.

**Head\_dim determines how big each key/value is**  
Each KV head stores a fixed-size block of numerical data for every token. The size of the block is referred to as the head dimension. The head dimension is determined by how the model’s internal representation of a token is split across attention heads. To understand this, it helps to introduce the concept of hidden size.

The term hidden size comes from earlier neural network designs, in which models were described by input layers, output layers, and internal (or hidden) layers. In this context, hidden simply means internal to the model, i.e., not directly visible to the user. In modern transformer models, hidden size refers to the total size of the model’s internal representation of a token. In practical terms, it defines how much numerical information the model maintains for each token as it processes a prompt.

Llama 3.1 has a hidden size of 8192, which means that for every token, the model maintains 8192 numerical values as its internal valuation. During attention, this internal representation is not used as a single block. Instead, it is divided evenly among the model's attention heads, allowing it to process different aspects of the token's information in parallel.

* * *

This design also explains why GPUs are so effective for the transformer models. Once the internal representation is split across attention heads, each head can be processed largely independently. GPUs are optimized for executing many similar operations in parallel across independent data blocks. Attention heads naturally fit this execution model, allowing the GPU to process multiple heads simultaneously with high throughput.

From a system perspective, this means that increasing the number of heads increases parallel work, not sequential complexity, a pattern that maps well to GPU architectures. Because attention heads operate independently, they form natural units of parallel execution. As models scale beyond a single GPU, the number and organization of heads directly influence how work can be distributed across multiple GPUs. A topic later discussed in another article.

* * *

The size of the portion assigned to each head is the head dimension, which is calculated by dividing the hidden size by the number of attention heads. For Llama 3.1 70B, the hidden size is 8192, it has 64 attention heads. This means that the internal representation of each token is split into 64 equal parts: 8192 / 64 = 128. As a result, each KV head stores 128 numerical values per token, per layer, for keys and for values.

**Why does the calculation use KV Heads with GQA involved**  
So far, we have explained how keys and values are stored per token, per layer, and per head. The remaining question is why the calculation uses the number of KV heads, rather than the total number of attention heads. In GQA, Llama 3.1 70B, the multiple query heads share the same key-value data.

The 64 query heads independently determine relevance, but those queries are mapped onto only 8 shared sets of keys and values. Because the key and value data is shared in this way, only 8 KV heads need to be stored per token, which is why the KV cache calculation uses ‘Kv\_heads = 8’ rather than the total number of attention heads.

**Tying the architecture back to the formula**  
With these components in place, we can now return to the KV cache memory calculation and see how each part of the formula directly maps to the model architecture. For each token, the model stores key and value data:

- Across 80 layers, because each layer maintains its own attention state

- Across 8 KV heads, because GQA maps 64 query heads onto 8 shared sets of key and value data

- With 128 numerical values per head, determined by how the model’s internal representation is split across attention heads

- At 2 bytes per value, because keys and values are stored in FP16

This leads directly to the per-token KV cache size:

2 (Key + Value) x 80 (Layers) x 8 (KV heads) x 128 (head dimension) x 2 bytes = 327,680 bytes x 131,072 tokens = 42.95GB KV cache memory, excluding the model's weights and temporary activations.

**The concurrency trade-off**  
While the math gives us a clear number, such as the 42.95GB required for a full 128K context on this model, its true value lies in its power to transform how we plan services. In production, we aren’t just deploying a model; we are deploying a memory budget. The fundamental architectural goal of this exercise is to move a service level from probabilistic to deterministic concurrency.

**Establishing the baseline floor**  
In a live environment, prompts are unpredictable. One user might send a 500-token prompt, while another triggers a RAG retrieval that generates 15.000 tokens. If an architect plans only for average usage, the system remains in a probabilistic state, in which performance guarantees are impossible.

By calculating the memory required for the desired maximum context length, we establish a deterministic floor on the number of concurrent users. This is the guaranteed number of sessions the GPU/model can support simultaneously, even in the worst-case scenario in which every user hits their maximum limit at once.

This floor becomes the baseline for future monitoring. By comparing this deterministic baseline against real-world telemetry, teams can see exactly how many additional ‘practical’ concurrent users a GPU actually serves, given that the average prompt is shorter than the maximum.

**The data scientist lever**  
This is why data scientists and architects often actively test and reduce the maximum content length. By constraining the context window, they can significantly increase the total number of users a single system can serve simultaneously.

Reducing the maximum context length from 128K to 8K essentially reduces the ‘reserved’ memory per user. This immediately increases the deterministic number of users we can guarantee. Reducing the maximum context length allows the business to decide the trade-off. Do we need a few users with massive context windows (i.e., is that required by the workload?), or is it more valuable to have a higher deterministic floor for many users with shorter (8K) context windows?

By grounding the deployment in these calculations,, we move away from reacting to memory issues/ lower response times and towards a strategy of guaranteed capacity planning.

**The infrastructure parallel**  
For vAdmins, this mirrors the strategy of maintaining a 1-to-1 mapping of physical to virtual system memory during normal operations to eliminate overcommitment risks. However, we still enjoy the benefits of over-consolidation during critical infrastructure events, such as maintenance mode or HA failover events.

Because real-world prompts are probabilistic and often stay well below the maximum token limit, the deterministic floor we’ve calculated can actually serve as a massive safety buffer. It allows you to safely over-consolidate user sessions onto fewer GPUs during a failover, relying on average usage patterns to keep the system standing while the physical infrastructure is being serviced.

It is important to acknowledge that maintaining this safety buffer comes at a high cost. Because GPUs are extremely high-cost assets, planning solely for deterministic ‘worst-case’ can lead to under-utilized hardware and inflated budgets. This is why the dialogue between infrastructure architects and data science teams is so critical. Together, the teams must determine the right cost factor, finding a middle ground where the context window is large enough to be useful, but constrained enough to ensure service resilience and hardware efficiency. By aligning the context window with actual organizational needs, we ensure that every byte of RAM drives value rather than just sits in reserve.

**Quantization Impact**  
Quantizing a model (for example, to FP8) primarily affects model weight and compute precision. Keys and Values stored in the KV cache are still FP16 by default, unless the inference stack explicitly supports and enables FP8 KV cache. In other words, the KV cache precision is a runtime choice, not a model property. From a memory perspective, this means that quantizing weights alone does not reduce KV cache memory consumption

**Temporary activation memory**  
In addition to the KV cache, inference also requires temporary activation memory. These activations hold intermediate results while the model processes tokens, such as query representations and intermediate attention outputs.

Unlike the KV cache, activation memory is short-lived. It is allocated during computation and released immediately after use. As a result, activation memory does not grow with context length. Activation memory is most significant during the prefill phase, when the entire prompt is processed at once. During token-by-token decoding (decode phase), activation memory usage is relatively small and stable.

**Applying the formula to your model of interest**  
Once the calculation is understood for this specific model, applying the same approach to your model of interest is relatively straightforward. All modern transformer models expose the required parameters in their model configuration, typically through a config.json file. Please only refer to that file or an equivalent runtime object, as it is the single source of truth. Many online GPT services easily hallucinate. To determine the KV cache memory footprint, we need to identify the following:

| **What we need** | **Common config field names** |
| --- | --- |
| Layers | Num\_hidden\_layers, n\_layers |
| Hidden size | Hidden\_size, d\_model |
| Attention heads | Num\_attention\_heads, n\_heads |
| KV heads | num\_key\_value\_heads |
| GQA | Num\_key\_value\_heads < num\_attention\_heads |
| KV precision | Runtime / inference setting |
| Maximum context length | Max\_position\_embeddings |

If a model uses GQA, there is typically a separate key/value head count listed in the file. The head dimension can then be derived by dividing the hidden size by the number of attention heads. If a model does not explicitly define a separate number of key/value heads, it can be assumed that each attention head has its own keys and values, resulting in higher KV cache memory usage.

### Conclusion: Balancing Resilience and ROI

Ultimately, this sizing exercise is about transforming the way we plan and monitor services. By calculating your "worst-case" KV cache, we effectively establish a 1-to-1 mapping of physical to virtual memory during normal operations. This ensures that our 'steady-state' performance is guaranteed and predictable.

However, because GPUs are extremely high-cost assets, this safety buffer must be balanced against hardware efficiency. Planning solely for the absolute "worst-case" can lead to under-utilized hardware and inflated budgets. This is why the dialogue between infrastructure architects and data science teams is so critical. Together, you must determine the right cost factor, finding a middle ground where the context window is large enough to be useful but constrained enough to ensure that every byte of VRAM drives actual organizational value.
