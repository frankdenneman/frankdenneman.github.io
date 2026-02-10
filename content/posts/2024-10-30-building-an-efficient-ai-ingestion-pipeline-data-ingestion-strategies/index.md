---
title: "Building an Efficient AI Ingestion Pipeline: Data Ingestion Strategies"
date: 2024-10-30T09:00:00+01:00
draft: false
categories: ["ai"]
tags: ["RAG", "LLM", "Ingestion", "Vector Database", "Batch", "Streaming", "MLOps"]
---

Traditionally, deploying applications is a straightforward process that moves from development to production. For instance, enterprise apps usually work with databases to perform standard tasks, which makes resource management and maintenance predictable. Generative AI (Gen-AI) applications, however, are more flexible and complex. They need to adapt quickly, since they work with constantly changing data and must handle a wide range of demands. Gen-AI apps, especially those using Large Language Models (LLMs) and Retrieval Augmented Generation (RAG), don’t follow the same linear path as traditional workloads. Instead, they move through a circular, adaptive lifecycle with two main stages: research and production.

Understanding these two phases is crucial for infrastructure administrators who manage and scale AI-driven applications. This requires an approach that supports continuous change and adaptation rather than a single, linear deployment.

## Research phase

The research phase in Gen-AI workloads is like a continuous lab experiment. Here, data scientists keep testing models, adjusting algorithms, and trying out different setups to find the best balance of accuracy, efficiency, and flexibility. This phase moves quickly and values flexibility over stability. For example, a data scientist might change the chunk size or try new indexing methods in a vector database to speed up retrieval. Often, it takes several rounds of testing to see what works best for each dataset.

To work flexibly, data scientists need to manage their own resources. They should have easy access to set up things like Deep Learning VMs, AI Kubernetes clusters, and Vector Databases. When they can do this themselves, they can quickly adjust to new discoveries and keep experimenting without waiting for help from infrastructure teams.

## Production phase

The production phase is about getting the Gen-AI application ready for real-world use. The main goals here are scalability, reliability, and steady performance, so the system can meet user needs. At this stage, the infrastructure must support stable and efficient operations as the app moves from testing to serving many users.

In this phase, the lessons learned during research help build production-ready systems. While research focuses on flexibility, production is all about reliability and predictability. Workloads are set up for speed and stability, so the app can handle lots of user queries, manage new data smoothly, and give accurate answers every time.

Containerized platforms are key in this phase because they let you package the app in a consistent environment that’s easy to scale. Platforms like Kubernetes allow for horizontal scaling, either automatically or with help from DevOps teams, so workloads can grow as demand increases. For example, if user traffic spikes, new containers can be started to handle the extra load and keep the user experience smooth.

## Data ingestion strategies

Data ingestion is a key part of Gen-AI workflows, providing the RAG system with the data it needs to generate useful responses. Depending on whether you’re in the research or production phase, different ingestion strategies are used. Here are the three main types:

Automated batch ingestion is good for handling large amounts of data on a set schedule, without needing manual work. It’s ideal for processing lots of information during off-peak hours, so updates to the knowledge base are regular and predictable. For example, a company with a big, unchanging dataset like product catalogs or research papers can use batch ingestion to update its system every night. This method helps infrastructure admins plan CPU, memory, and storage use, especially during scheduled low-traffic times.

Streaming ingestion works nonstop, bringing in real-time changes so the system always has the latest information. This is especially useful for time-sensitive apps where it’s important to keep delays low. However, streaming can lead to unpredictable resource needs. ML Ops teams need to watch and manage resources closely to avoid slowdowns, especially when there’s a lot of data coming in. Using cluster services like DRS and choosing the right VM types helps keep resources available.

Manual ad-hoc ingestion lets you process specific data on demand, giving you a lot of control and flexibility. It’s useful when you need to add important information right away, like new legal rules or emergency alerts. While this method gives precise control, it doesn’t scale well for large or frequent updates and needs human input. Infrastructure admins should know that ad hoc ingestion can cause sudden spikes in resource use, which might affect other processes if the system isn’t flexible enough.

## Production data ingestion strategies

Automated batch and streaming ingestion are mainly used in production, where a steady and reliable flow of data is needed to keep the model current and accurate.

When looking at how ingestion affects infrastructure and resource use, the data window and peak throughput are key. They determine how well resources are used and how fresh the data stays.

### Data Window

The data window is the period when data is collected, processed, and brought into the system. Having a clear data window helps manage batch jobs efficiently. How long this window is can have a big impact on infrastructure needs:

**Short Data Window:** With a short data window, ingestion jobs happen more often, so smaller batches are processed each time. This lowers latency and allows for near-real-time updates, but it also means more frequent jobs to manage. The infrastructure must be flexible enough to handle bursts of activity, making sure compute, memory, and network resources are available when needed.

**Long Data Window:** A long data window means bigger batches are processed less often, which cuts down on the overhead of frequent jobs. But processing more data at once can put a lot of pressure on storage, compute, and I/O resources during those times. The infrastructure needs to handle these peak demands efficiently.

![Data window processes](images/data-window-processes.png)

Another important factor is the data volume multiplication that happens during ingestion, as data is extracted, transformed, and loaded into the vector database. The intermediate data is usually kept in memory or storage. When working with large datasets and long data windows, it’s important to clean up properly. The next article explains data volume multiplication in more detail.

### Peak Throughput

Peak throughput is the highest amount of data the system needs to handle during ingestion. Knowing and managing this is key to keeping the system running smoothly and avoiding slowdowns:

**Compute Resources:** During peak times, CPU use can be high but often goes up and down, mostly because of how data is transferred and processed. As data moves from different sources into storage or memory, CPU load can spike, depending on the tools used for ingestion and transformation. These tools might not be fully optimized, so CPU use can vary a lot. For example, a performance graph might show that even if a machine has 16 cores, only 4 are used at a time, even when the process is set to use all 16.

![CPU activity](images/cpu-activity.png)

There are different ways to handle batch ingestion, and each affects CPU and resource use differently. One method is to collect all new data from every source before moving to the next step. This approach gathers data in a set time frame, causing high CPU and I/O activity at first, then moves on to processing. This way, the GPU-based embedding model can use parallel processing fully. Resource use spikes during each phase, but it stays manageable.

Another way is to process each data source one at a time, finishing the whole ingestion pipeline for one dataset before starting the next. This serial method means each source is fully ingested, transformed, and stored before moving on. It often leads to short bursts of heavy resource use, followed by quieter periods. CPU and GPU use can change a lot during this, depending on the data and the tools.

In both cases, resource use is spiky, with short bursts of high CPU and memory use followed by idle times. How long these idle periods last depends on the method, data size, and processing speed. For infrastructure admins, knowing about these spikes is important for planning resources, whether by reserving CPU for peak times or relying on DRS and cluster idleness to adjust as needed.

To support these workflows well, infrastructure planning should consider the uneven peaks in CPU and memory use during ingestion. This means providing enough burst capacity, timing workloads to avoid clashing with other important tasks, and thinking about using dynamic scaling or resource quotas to reduce waste while staying flexible.

By noticing the uneven, high-demand resource patterns during the data window, infrastructure admins can make better decisions to keep the data pipeline running smoothly.

**Storage I/O:** Peak throughput affects storage needs, especially I/O operations per second (IOPS). High-throughput ingestion creates lots of read and write actions, especially when embeddings are made and saved in real time. To prevent I/O slowdowns, it’s important to have high IOPS, like with an all-flash storage platform that can handle many users at once.

**Network Bandwidth:** Ingestion often means moving data between storage, processing nodes, and sometimes outside sources. High peak throughput puts pressure on network bandwidth, especially if lots of data comes from different places. Making sure the network has enough capacity, or timing ingestion to avoid busy periods, helps prevent slowdowns and keeps performance steady.

**Memory Utilization:** Memory usage can spike during peak ingestion, particularly if data transformations, such as chunking or embedding generation, require large amounts of CPU and GPU memory. The system needs enough RAM to handle this without causing too much swapping or memory thrashing, which would hurt performance.

Data freshness means how fast updates from data sources show up in the system, which affects how relevant and accurate Gen-AI apps are in production. When up-to-date info is crucial, like in customer support, the delay between updates and ingestion should be as short as possible. Frequent updates may need shorter ingestion times, while less important updates can wait for off-peak hours to ease the load.

The timing of data ingestion should also fit the work patterns of global teams. Planning ingestion for after-office hours, like updating Confluence pages at night, means the Gen-AI has all new data by the next workday. But in global companies, work happens in all time zones, so there’s no single quiet period. To solve this, you can stagger ingestion times based on regional work hours or use micro-batching—running small, frequent ingestions all day—to spread out the load and keep data fresh.

It’s important to manage infrastructure load carefully, making sure there’s enough capacity for ingestion without affecting other services. Scheduling ingestion during low-usage times, when computing and storage needs are lowest, helps avoid resource conflicts and keeps things running smoothly. In a global setup, using cloud infrastructure to ingest data closer to its source can also boost throughput and cut down on delays.

It’s also important to think about how often different data sources change and how important they are. Internal documents might need frequent updates, while external datasets or archives may only need occasional ingestion. Setting ingestion schedules based on how often each source updates helps keep things efficient and fresh. Prioritizing key content, like customer-facing docs, makes sure the most important info is always current.

In the end, successful data ingestion for an RAG pipeline means balancing data freshness, infrastructure efficiency, and user needs. Scheduling should be flexible for global use and able to adapt as things change. By keeping an eye on activity and adjusting batch schedules as needed, infrastructure teams can make sure data is ingested efficiently and the knowledge base stays current in a fast-changing environment.

## Research data ingestion strategies

During the research phase, data ingestion is more flexible and experimental, often using manual ad hoc methods. Data scientists try different sources, formats, and methods for bringing in data to see how they affect model performance.

However, some elements of automated batch processing can be mimicked in the research phase by using scripts on (Jupyter) notebooks to perform bulk data loads on a trial basis. These ad-hoc batch loads provide insights into resource needs, data processing times, and scalability considerations, helping data scientists refine ingestion methods before implementing them in production. In this way, the research phase serves as a proving ground, where different ingestion strategies are tested and optimized for optimal performance when transitioned to production.

## Conclusion

In summary, managing resources and peak throughput during the data window means understanding that resource demands can be spiky and unpredictable. Infrastructure admins should use smart scheduling, dynamic scaling, and effective capacity planning to address these challenges effectively.
