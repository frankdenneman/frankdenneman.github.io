---
title: "Retrieval-Augmented Generation Basics for the Data Center Admin"
date: 2024-01-16T09:00:00+01:00
draft: false
slug: "retrieval-augmented-generation-basics-for-the-data-center-admin"
categories: ["ai"]
tags: ["RAG", "LLM", "Vector Database", "Embeddings", "Data Center"]
---

Thanks to ChatGPT, Large Language Models (LLMs) have caught the attention of people everywhere. When built into products and services, LLMs can make most interactions with systems much faster.

Current LLM-enabled apps mostly use open-source LLMs such as **[Llama 2](https://ai.meta.com/llama/)**, **[Mistral](https://mistral.ai/news/announcing-mistral-7b/)**, **[Vicuna](https://lmsys.org/blog/2023-03-30-vicuna/)**, and sometimes even **[Falcon 170B](https://huggingface.co/tiiuae/falcon-180B)**. These models are trained on publicly available data, allowing them to react appropriately to most prompts. Yet organizations often want LLMs to respond using domain-specific or private data.

In that case, a data scientist can fine-tune the model by providing additional examples. Fine-tuning builds on the model’s existing capabilities. Techniques such as **[LoRA](https://arxiv.org/abs/2106.09685)** freeze the model’s weights and add small, trainable adapter layers focused on domain-specific needs. Hugging Face recently **[published an article](https://huggingface.co/blog/Lora-for-sequence-classification-with-Roberta-Llama-Mistral)** showing that LoRA introduces only 0.12% additional parameters for Llama 2 7B—about 8.4 million parameters. This means fine-tuning can often be done using just a pair of data center GPUs.

This is why, at VMware at Broadcom, we believe combining open-source LLMs with fine-tuning is a practical path toward building strategic business applications.

However, each time a new product or service is launched, a data scientist must gather information, organize the data, and fine-tune the model again so it can answer new questions accurately.

## Introducing Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) offers a faster, more flexible alternative. RAG adds database capabilities to an LLM, allowing it to retrieve relevant information dynamically while generating an answer. Instead of retraining or fine-tuning the LLM every time new data appears, the model can access up-to-date information directly.

Adding RAG to an LLM-enabled application requires more than just connecting a database. Additional steps are involved, but thanks to ongoing work in the data science community, building RAG systems is becoming more accessible. At VMware, this approach is central to the development of VMware Private AI Foundation.

Let’s first look at how a basic (non-RAG) LLM workflow operates. A user submits a prompt in an application (1). The app sends the prompt to the LLM (2). The LLM generates a response (3), which the app then displays to the user (4).

![Basic LLM workflow](images/retrieval.png)

## Vector Databases: The Core of RAG

Before diving deeper into RAG, it’s important to understand the vector database. Unlike traditional databases with rows and columns, a vector database stores numerical representations of data, known as vector embeddings. These vectors are grouped based on similarity.

Neural network models such as LLMs can only process numbers. In the Natural Language Processing (NLP) pipeline, words are converted into tokens, which are then represented as vectors. These vectors capture the meaning of words and their relationships to other words. For a deeper explanation, Sasha Metzger’s article **[A Beginner's Guide to Tokens, Vectors, and Embeddings in NLP](https://medium.com/@saschametzger/what-are-tokens-vectors-and-embeddings-how-do-you-create-them-e2a3e698e037)** is highly recommended.

With RAG, the vector database effectively becomes the LLM’s long-term memory. To populate this memory, data is converted into tokens and then into vector embeddings. Tools such as Word2Vec, fastText, and GloVe can be used for this purpose, while frameworks like LlamaIndex help manage ingestion, indexing, and retrieval. Data can be vectorized asynchronously, allowing new information to be added without retraining or fine-tuning the LLM.

## How RAG Works in Practice

From a user’s perspective, the workflow changes slightly. The user submits a prompt in the application (1). Instead of sending the prompt directly to the LLM, the app queries the vector database (2). The vector database performs a similarity search and retrieves relevant data (3). This data is sent back to the application, which augments the user’s prompt with the retrieved context (4). The application then instructs the LLM to generate a response using both the original prompt and the retrieved data (5). Finally, the app presents the response to the user (6).

![Retrieval-augmented generation workflow](images/augmented-generation.png)

RAG behaves much like a theater prompter, or *souffleur*. Just as a prompter provides cues to actors during a play, RAG provides contextual cues to the LLM. The vector database acts as the system of record, while the LLM and application layer provide the intelligence to generate accurate, context-aware responses.
