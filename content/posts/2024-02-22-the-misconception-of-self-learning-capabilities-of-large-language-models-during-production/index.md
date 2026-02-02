---
title: "The misconception of self-learning capabilities of Large Language Models during Production"
date: 2024-02-22
categories: 
  - "ai"
coverImage: "1699963356933.jpeg"
---

I enjoyed engaging with many customers about bringing Gen-AI to the on-prem data center at VMware Explore. Many customers want to keep their data and IP between the four walls of their organization, and rightly so.

With VMware Private AI Foundation, we aim to utilize foundation models and build upon the great work of many smart data scientists. Foundation models like [Llama 2](https://ai.meta.com/llama/), [StarCoder](https://huggingface.co/blog/starcoder), and [Mistral 7b](https://mistral.ai/news/announcing-mistral-7b/). Instead of building and training a large language model (LLM) from the ground up, which can be time-consuming and computationally expensive, organizations can leverage foundation models pre-trained on a massive dataset of text and code. If necessary, organizations can further fine-tune a foundation model on specific tasks and data in a short period of time.

At VMware, we believe in using [Vector DB](https://cloud.google.com/discover/what-is-a-vector-database)s with [Retrieval Augmented Generation](https://core.vmware.com/resource/vmware-private-ai-starter-pack-retrieval-augmented-generation-rag-systems#introduction) (RAG) to decouple the IP and data from the foundation model. Using RAG, you offload the knowledge updates to another system so the Gen-AI application is always up to date. The vector DB is used for memorizing facts, while the foundation model is used for reasoning functionality. If necessary, the foundation model can be replaced by a newer version. Typically, this doesn't happen, but if a data science team thinks it will improve the Gen-AI application's reasoning or generative capability, they can do that without losing any IP.

And this particular fact, not losing any IP by replacing the model, got me some pushback from the people I spoke to. By digging into this topic a bit more, I discovered misconceptions among many about the learning ability of a neural network (LLM) model.

When you use an LLM, i.e., asking it a question (prompt), the model does NOT learn from your question. LLMs have no self-learning mechanisms during the deployment phase (inference). Let's dive a bit deeper into the difference between inference and training.

**Inference:** When asking a model a question, you ask it to make a prediction, and the model feeds the input data to the network and its weights (parameters) to compute the output. This sequence is also called a forward pass.

Data scientists freeze the parameters when the neural network is accurate enough, and inference uses the same parameters for every question during inference.

**Training:** When training a neural network, the first step is called the forward pass, which is the same as inference. The forward pass calculates the prediction of the model for the input data. After the forward pass, the loss is calculated by comparing the prediction to the expected result. The loss is used to calculate a gradient. The gradient guides the framework to increase or decrease the values of each parameter. The Backpropagation pass adjusts the parameters layer by layer to minimize the loss.

The training process repeats the forward pass and backpropagation until the model converges, meaning the loss no longer decreases. Once the model converges, a checkpoint is created, and the parameters are frozen. The Gen-AI application uses this version of the model to generate answers.

I believe the misconception of self-learning capabilities occurs when thinking about either recommender systems (Netflix proposing which series to look at next or Amazon telling you other customers bought item X along with item Y), but a recommender system uses a converged model (frozen weights), with an online feature store. An online feature store provides real-time access to essential features for generating accurate and personalized recommendations. Amazon uses an online feature store to store features about its products and users.

- **Product features:** These describe the products themselves, such as their price, category, popularity, brand, color, size, rating, and reviews.

- **User features:** These describe the users, such as their past purchase history, demographics (age, gender, location), interests, and browsing behavior.

Suppose an Amazon customer has purchased many books in the past. In that case, the recommender system might recommend other books to the user based on collaborative or content-based filtering. With collaborative filtering, the algorithm identifies users with similar tastes to the target user and recommends items that those users have liked. With content-based filtering**,** the algorithm recommends items similar to items the target user has liked in the past. It seems like the model is learning when using it. In reality, the model really calculates predictions by using its parameters and data (features) from the online feature store (a database).

The [context window](https://docs.kanaries.net/topics/ChatGPT/chatgpt-context-window) is another example of why a Gen-AI application like ChatGPT seems to be learning while using it. Models can appear to "learn" during inference in the same context, but it is because the same information is still part of its context window. The best analogy for an LLM context window is the working memory of a human. For example, if I ask [Llama 2](https://ai.meta.com/llama/), "Who is the CEO of VMware?" and the answer it returns is "Pat Gelsinger," and I respond with, "No, it's Raghu," and it responds with, "Yes, that is correct, the CEO of VMware is Raghu Raghuram." Then, if I ask it, "Who is the CEO of VMware?" it will respond with "Raghu Raghuram," but that is only because the same context has the answer. Google's Bard supports up to 2048 tokens, and ChatGPT supports up to 4096 tokens. By default, Llama 2 has a context window of 4096 tokens, but [Huge Llama 2](https://medium.com/@sushilkumar467/huge-llama-2-with-32k-context-length-9f7e11853d03) supports up to 32K tokens. A token is a unit of text that the model uses to process and generate text. Tokens can be words, subwords, or characters.

Everything comes at a price. The larger the context window is, the more memory and compute inference are consumed. Outside of the same conversational context, models are completely stateless and cannot permanently "learn" anything in inference mode. What most LLMaaS do is capture the user prompts, which might contain sensitive data, and use it to form training data sets. On top of that, they use a technique called [Reinforcement Learning with Human Feedback](https://huggingface.co/blog/rlhf) (RHLF), which allows it to learn more frequently. Chip Huyen published an [excellent article describing RLHF](https://huyenchip.com/2023/05/02/rlhf.html) in detail while being understandable for non-data-scientists.

Why does this distinction matter of self-learning matter for non-data scientists? By understanding that default foundation models do not alter state during use, VI-admins, architects, and application developers can design an infrastructure and application that offers high availability while offering a proper life cycle management strategy for the Gen-AI application.

For example, the checkpoint of a model can be loaded and exposed by an inference framework running in separate VMs on separate accelerated ESXi hosts with an anti-affinity rule that ensures that each model API endpoint will not share the same physical infrastructure to reduce the blast radius. A load-balancer in front of the inference frameworks offers the flexibility to take one inference framework offline during maintenance jobs without seeing some behavior change. As the model is frozen, no model version would have learned more than the other during their service time.

We are currently building and developing VMware Private AI Foundation to allow VMware customers to deploy LLMs on-prem securely and keep the data and Gen-AI application access secure. Private data should be kept private, and together with using state-of-the-art foundation models, organizations can safely build their Gen-AI applications to support their business goals.

A special thanks goes out to [@Steve Liang](https://www.linkedin.com/in/steve-l-7775071a/) for making this article more informative.
