---
title: "My Picks for NVIDIA GTC Spring 2023"
date: 2023-03-21
categories: 
  - "ai"
coverImage: "Screenshot-2023-03-14-at-09.05.54.png"
---

This week GTC Spring 2023 kicks off again. These are the sessions I look forward to next week. Please leave a comment if you want to share a must-see session.

* * *

## MLOps

Title: [Enterprise MLOps 101 \[S51616\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666629510665001N7VV)

The boom in AI has seen a rising demand for better AI infrastructure — both in the compute hardware layer and AI framework optimizations that make optimal use of accelerated compute. Unfortunately, organizations often overlook the critical importance of a middle tier: infrastructure software that standardizes the machine learning (ML) life cycle, adding a common platform for teams of data scientists and researchers to standardize their approach and eliminate distracting DevOps work. This process of building the ML life cycle is known as MLOps, with end-to-end platforms being built to automate and standardize repeatable manual processes. Although dozens of MLOps solutions exist, adopting them can be confusing and cumbersome. What should you consider when employing MLOps? How can you build a robust MLOps practice? Join us as we dive into this emerging, exciting, and critically important space.

[Michael Balint](https://www.linkedin.com/in/mbalint?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAMHjrwBb6PkPNw-iz1EQcLEfF0C9onTyAs), Senior Manager, Product Architecture, NVIDIA

[William Benton](https://www.linkedin.com/in/willbenton?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAH7lu0BtrZhyGes6jzSm3ojEarGDcmbb-Q), Principal Product Architect, NVIDIA

Title: [Solving MLOps: A First-Principles Approach to Machine Learning Production \[S51116\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1665668292384001djwv)

We love talking about deploying our machine learning models. One famous (but probably wrong) statement says that “87% of data science projects never make it to production.” But how can we get to the promised land of "Production" if we're not even sure what "Production" even means? If we could define it, we could more easily build a framework to choose the tools and methods to support our journey. Learn a first-principles approach to thinking about deploying models to production and MLOps. I'll present a mental framework to guide you through the process of solving the MLOps challenges and selecting the tools associated with machine learning deployments.

[Dean Lewis](https://www.linkedin.com/in/saintdle?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAABU24foBBmBIg9NuWcjKWa7JwL83L6PGU68) Pleban, Co-Founder and CEO, DagsHub

Title: [Deploying Hugging Face Models to Production at Scale with GPUs \[S51553\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666618732882001vF5e)

Seems like everyone's using Hugging Face to simplify and reuse advanced models and work collectively as a community. But how do you deploy these models into real business environments, along with the required data and application logic? How do you serve them continuously, efficiently, and at scale? How do you manage their life cycle in production (deploy, monitor, retrain)? How do you leverage GPUs efficiently for your Hugging Face deep learning models? We’ll share MLOps orchestration best practices that'll enable you to automate the continuous integration and deployment of your Hugging Face models, along with the application logic in production. Learn how to manage and monitor the application pipelines, at scale. We’ll show how to enable GPU sharing to maximize application performance while protecting your investment in AI infrastructure and share how to make the whole process efficient, effective, and collaborative.

[Yaron Haviv](https://www.linkedin.com/in/yaronh?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAACTySEBqFfCS39Y3bCPOktcnoyFlCAxAxc), Co-Founder and CTO, Iguazio

Title: [Democratizing ML Inference for the Metaverse \[S51948\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666656012157001Xk7x)

In this talk, I will drive you through the Roblox ML Platform inference service. You will learn how we integrate Triton inference service with Kubeflow and Kserve. I will describe how we simplify the deployment for our end users to serve models on both CPU and GPUs. Finally, I will highlight few of our current cases like game recommendation and other computer vision models.

[Denis Goupil](https://www.linkedin.com/in/denis-goupil?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAABe9IJcBWFugiCCRfrkVGPzgHWceEVnLx9U), Principal ML Engineer, Roblox

* * *

## Data Center / Cloud

Title: [Using NVIDIA GPUs in Financial Applications: Not Just for Machine Learning Applications \[S52211\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1671664686639001fQzH)

Deploying GPUs to accelerate applications in the financial service industry has been widely accepted and the trend is growing rapidly, driven in large part by the increasing uptake of machine learning techniques. However, banks have been using NVIDIA GPUs for traditional risk calculations for much longer, and these workloads present some challenges due to their multi-tenancy requirements. We'll explore the use of multiple GPUs on virtualized servers leveraging NVIDIA AI Enterprise to accelerate an application that uses Monte Carlo techniques for risk/pricing application in a large international bank. We'll explore various combinations of the virtualized application on VMware to show how NVIDIA AI Enterprise software runs this application faster. We'll also discuss process scheduling on the GPUs and explain interesting performance comparisons using different VM configs. We'll also detail best practices for application deployments.

[Manvender Rawat](https://www.linkedin.com/in/manvender?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAATccUYBeItrg0AHrHktDPwM7E_I4i1Hgos), Senior Manager, Product Management, NVIDIA

[Justin Murray](https://www.linkedin.com/in/justin-murray-6118481?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAABNbW0BxJh5B_3tmWJILr7iGtiT6GzhBik), Technical Marketing Architect, VMware

Richard Hayden, Executive Director and Head of the QR Analytics Team, JP Morgan Chase

Title: [AI in the Clouds: Navigating the Hybrid Sky with Ease (Presented by Run:ai) \[S52352\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1674031430799001gBiK)

We'll focus on the different use cases of running AI workloads in hybrid cloud and multi-cloud environments, and the challenges that come along with that. NVIDIA's Michael Balint Run:ai's and Gijsbert Janssen van Doorn will discuss how organizations can successfully implement a hybrid cloud strategy for their AI workloads. Examples of use cases include leveraging the power of on-premises resources for sensitive data while utilizing the scalability of the cloud for compute-intensive tasks. We'll also discuss potential challenges, such as data security and compliance, and how to navigate them. You'll gain a deeper understanding of the various use cases of hybrid cloud for AI workloads, the challenges that may arise, and how to effectively implement them in your organization.

[Michael Balint](https://www.linkedin.com/in/mbalint?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAMHjrwBb6PkPNw-iz1EQcLEfF0C9onTyAs), Senior Manager, Product Architecture, NVIDIA

[Gijsbert Janssen van Doorn](https://www.linkedin.com/in/gijsbertjvd?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAADgaIABe_-GT64zURcVfI893dWpQHPNMhA), Director Technical Product Marketing, Run:ai

Title: [vSphere on DPUs Behind the Scenes: A Technical Deep Dive (Presented by VMware Inc.) \[S52382\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1674490572194001eyTN)

We'll explore how vSphere on DPUs offloads traffic to the data processing unit (DPU), allowing for additional workload resources, zero-trust security, and enhanced performance. But what goes on behind the scenes that makes vSphere on DPUs so good at enhancing performance? Is it just adding a DPU? Join this session to find the answer and more technical nuggets to help you see the power of DPUs with vSphere on DPUs.

[Dave Morera](https://www.linkedin.com/in/greatwhitetec?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAL74AgBk1pL5xzm9yVzYKNenj1XkBX1jPs), Senior Technical Marketing Architect, VMware

[Meghana Badrinath](https://www.linkedin.com/in/megbadri?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAA4dDI4BaSTkpzgxAccVYPm_xyYLqF0MmWU), Technical Product Manager, VMware

Title: [Developer Breakout: What's New in NVAIE 3.0 and vSphere 8 \[SE52148\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1670877390176001xuxy)

NVIDIA and VMware have collaborated to unlock the power of AI for all enterprises by delivering an end-to-end enterprise platform optimized for AI workloads. This integrated platform delivers NVIDIA AI Enterprise, the best-in-class, end-to-end, secure, cloud-native suite of AI software running on VMware vSphere. With the recent launches of vSphere 8 and NVIDIA AI Enterprise 3.0, this platform’s ability to deliver AI solutions is greatly expanded. Let’s look at some of these state-of-the-art capabilities.

[Jia Dai](https://www.linkedin.com/in/daijia?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAThESYB03PlcGhRRcIvJgFBjP_Vc_R_kMo), Senior MLOps Solution Architect, NVIDIA

[Veer Mehta](https://www.linkedin.com/in/vmhta?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAADRMOgB1KDSpbd0deqH0LtR6MxMktJqC3s), Solutions Architect, NVIDIA

[Dan Skwara](https://www.linkedin.com/in/dan-skwara-9b5013127?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAB8l2tkBvObKs2zLVLtljV9g46aI3UqTcVU), Senior Solutions Architect, NVIDIA

* * *

## Autonomous Vehicles

Title: [From Tortoise to Hare: How AI Can Turn Any Driver into a Race Car Driver \[S51328\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666363422554001gSs3)

Performance driving on a racetrack is exciting, but it's not widely accessible as it requires advanced driving skills honed over many years. Rimac’s Driver Coach enables any driver to learn from the onboard AI system, and enjoy performance driving on racetracks using full autonomous driving at very high speeds (over 350km/h). We'll discuss how AI can be used to accelerate driver education and safely provide racing experiences at incredibly high speeds. We'll dive deep into the overall development pipeline, from collecting data to training models to simulation testing using NVIDIA DRIVE Sim, and finally, implementing software on the NVIDIA DRIVE platform. Discover how AI technology can beat human professional race drivers.

[Sacha Vrazic](https://www.linkedin.com/in/sacha-vrazic-0b45489a?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAABUU1ogBE5FS7pbQWN7EeDVX1booVQAEbWA), Director - Autonomous Driving R&D, Rimac Technology

* * *

## Deep Learning

Title: [Scaling Deep Learning Training: Fast Inter-GPU Communication with NCCL \[S51111\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1665650559668001nMtd)

Learn why fast inter-GPU communication is critical to accelerate deep learning training, and how to make sure your system has the right level of performance for your model. Discover NCCL, the inter-GPU communication library used by all deep learning frameworks for inter-GPU communication, and how it combines NVLink with high-speed networks like Infiniband to accelerate communication by an order of magnitude, allowing training to be run on hundreds, or even thousands, of GPUs. See how new technologies in Hopper GPUs and ConnectX-7 allow for NCCL performance to reach new highs on the latest generation of DGX and HGX systems. Finally, get updates on the latest improvements in NCCL, and what should come in the near future.

[Sylvain Jeaugey](https://www.linkedin.com/in/sylvain-jeaugey-255a7457?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAwU-2EBpuYrFxyf7bNt2UxRbr67vWRDj2o), Principal Engineer, NVIDIA

Title: [FP8 Mixed-Precision Training with Hugging Face Accelerate \[S51370\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666385471304001edqO)

Accelerate is a library that allows you to run your raw PyTorch training loop on any kind of distributed setup with multiple speedup techniques. One of these techniques is mixed precision training, which can speed up training by a factor between 2 and 4. Accelerate recently integrated Nvidia Transformers FP8 mixed-precision training which can be even faster. In this session, we'll dive into what mixed precision training exactly is, how to implement it in various floating point precisions and how Accelerate provides a unified API to use all of them.

[Sylvain Gugger](https://www.linkedin.com/in/sylvain-gugger-74218b144?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAACLo4mIBt1zVC6LyjTieyJ_gXro_zqiVVVw), Senior ML Open Source Engineer, Hugging Face

* * *

## HPC

Title: [Accelerating MPI and DNN Training Applications with BlueField DPUs \[S51745\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666643703564001vFWe)

Learn how NVIDIA Bluefield DPUs can accelerate the performance of HPC applications using message passing interface (MPI) libraries and deep neural network (DNN) training applications. Under the first direction, we highlight the features and performance of the MVAPICH2-DPU library in offloading non-blocking collective communication operations to the DPUs. Under the second direction, we demonstrate how some parts of computation in DNN training can be offloaded to the DPUs. We'll present sample performance numbers of these designs on various computing platforms (x86 and AMD) and Bluefield adapters (HDR-100Gbps and HDR-200 Gbps), along with some initial results using the newly proposed cross-GVMI support with DPU.

[Dhabaleswar K. (DK) Panda](https://www.linkedin.com/in/dhabaleswar-k-dk-panda-bab6892?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAB0s3MB5EZOLSK3aMrAP7b95wkKqmBhu7g), Professor and University Distinguished Scholar, The Ohio State University

Title: [Tuning Machine Learning and HPC Workloads Performance in Virtualized Environments using GPUs \[S51670\]](https://register.nvidia.com/flow/nvidia/gtcspring2023/attendeeportal/page/sessioncatalog/session/1666634502030001Ct4W)

Today’s machine learning (ML) and HPC applications run in containers. VMware vSphere runs containers in virtual machines (VMs) with VMware Tanzu for container orchestration and Kubernetes cluster management. This allows servers in the hybrid cloud to simultaneously host multi-tenant workloads like ML inference, virtual desktop infrastructure/graphics, and telco workloads that benefit from NVIDIA AI and VMware virtualization technologies. NVIDIA AI Enterprise software in VMware vSphere combines the outstanding virtualization benefits of vSphere with near-bare metal, or in HPC applications, better than bare-metal performance. NVIDIA AI Enterprise on vSphere supports NVLink and NVSwitch, which allows ML training, and HPC applications to maximize multi-GPU performance. We'll describe these technologies in detail, and you'll learn how to leverage and tune performance to achieve significant savings in total cost of ownership for your preferred cloud environment. We'll highlight the performance of the latest NVIDIA GPUs in virtual environments.

[Uday Kurkure](https://www.linkedin.com/in/ukurkure?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAAeVQgB6OqyFf_VKp4uvl_oOgw2O_L_NLc), Staff Engineer, VMware

[Lan Vu](https://www.linkedin.com/in/lanvu?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAASdWMEBuRCFKCq0m7fssikg2E7YqqsdQwU), Senior Member of the Technical Staff, VMware

[Manvender Rawat](https://www.linkedin.com/in/manvender?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAATccUYBeItrg0AHrHktDPwM7E_I4i1Hgos), Senior Manager, Product Management, NVIDIA
