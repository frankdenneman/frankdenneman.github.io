---
title: "5 Things to Know About Project Pacific"
date: 2019-08-26
coverImage: "project-pacific-medium.png"
---

During the keynote of the first day of VMworld 2019, Pat unveiled Project Pacific. In short, project Pacific transforms vSphere into a unified application platform. By deeply integrating Kubernetes into the vSphere platform, developers can deploy and operate their applications through a well-known control plane. Additionally, containers are now first-class citizens enjoying all the operations generally available to virtual machines.

![](images/project-pacific-1024x538.png)

Although it might seem that the acquisition of [Heptio](https://techcrunch.com/2018/11/06/vmware-acquires-heptio-the-startup-founded-by-2-co-founders-of-kubernetes/) and [Pivotal](https://www.cnbc.com/2019/08/22/vmware-earnings-q2-2020-acquires-carbon-black-pivotal.html) kickstarted project Pacific, VMware has been working on project Pacific for nearly three years! [Jared Rosoff](https://twitter.com/forjared ), the initiator or the project and overall product manager, told me that over 200 engineers are involved as it affects almost every component of the vSphere platform.

Lengthy technical articles are going to be published in the following days. With this article, I want to highlight the five key takeaways from project Pacific.

## 1: One Control Plane to Rule Them All

By integrating Kubernetes into the vSphere platform, we can expose the Kubernetes control plane to allow both developers and operation teams to interact with the platform. Instead of going through the hassle of installing, configuring, and maintaining Kubernetes clusters, each ESXi host acts as a Kubernetes worker node. Every cluster runs a Kubernetes control plane that is lifecycle managed by vCenter. We call this Kubernetes cluster the supervisor cluster, and it runs natively inside the cluster. This means that Kubernetes functionality, just like DRS and HA, is just a toggle switch away.

## 2: Unified Platform = Simplified Operational Effort

As containers are first-class citizens, multiple teams can now interact with them. By being able to run them natively on vSphere means they are visible to all your monitoring, log analytics, change management operations as well. This allows IT teams to move away from the dual-stack environments. Many IT teams that have been investing in Kubernetes over the last few years started to create a full operational stack beside the stack to manage, monitor, and operate the virtualization environment. Running independent and separate stacks next to each other is a challenge by itself.

However, most modern application landscapes are not silo'ed in either one of these stacks. They are a mix of containers, virtual machines, and sometimes even functions. Getting the same view across multiple operational stacks is near impossible. Project Pacific provides a unified platform where developers and operations share the same concepts. Each team can see all the objects across the compute, storage, and network layers of the SDDC. The platform provides a universal view with common naming and organization methods while offering a unified view of the complete application landscape.

## 3: Namespaces Providing Developer Self-service and Simplifying Management

Historically, vSphere is designed with the administrator group in mind as the sole operator. By exposing the Kubernetes API, developers can now deploy and manage their applications directly. As mentioned earlier, modern applications are a collection of containers and VMs, and therefore the vSphere Kubernetes API has been extended to support virtual machines, allowing the developer to use the Kubernetes API to deploy and manage both containers as well as virtual machines.

To guide the deployments of applications by the developers, project Pacific uses namespaces. Within Kubernetes, namespaces allow for resource allocation requirements and restrictions, and grouping of objects such as containers and disks. Withing project Pacific it's way more than that. In addition, these namespaces allow the IT ops team to apply policies to it as well. For example, in combination with Cloud-Native Storage (CNS), a storage policy can be attached to the namespace, providing a persistent volume with the appropriate service levels. For more info on CNS, check out Myles Gray's session: [HCI2763BU Technical Deep Dive on Cloud Native Storage for vSphere](https://my.vmworld.com/widget/vmware/vmworld19us/us19catalog?search=HCI2763BU)

Besides the benefits for the developers, as the supervisor cluster is subdivided into namespaces, they become a unit of tenancy and isolation. In essence, they become a unit of management within vCenter, allowing IT ops to resource allocation, policy management, and diagnostic and troubleshooting at namespace and workload level. As the namespace is now a native component within vCenter, it is intended to group every workload, both VMs, containers, and guest clusters and allow operators to manage it as a whole.

## 4: Guest Clusters

The supervisor cluster is meant to enrich vSphere, providing integrations with cloud-native storage and networking. However, the supervisor cluster is not an upstream conformant Kubernetes cluster. Guest clusters use the Kubernetes upstream cluster API for lifecycle management. It is an open system that's going to work with the whole Kubernetes ecosystem.

## 5: vSphere Native Pods providing lightweight containers with the isolation of VMs  

As we almost squashed the incorrect belief that ESXi is a Linux OS, we are now stating that containers are first-class citizens. Is ESXi after all a Linux OS, since you need to run Linux to operate containers? No ESXi is still not Linux, to run containers project Pacific is using a new container runtime called CRX.

Extremely simplified, a vSphere Native Pod is a virtual machine. We took out all the unnecessary components and run a lightweight Linux kernel and a small container runtime (CRX). To utilize our years of experience of paravirtualization, we optimized this CRX in such a way that it outperforms containers running on the traditional platforms. As Pat mentioned in the keynote, 30% faster than a traditional Linux VM and 8% faster than bare-metal Linux.

![](images/Pacific-Performance-1024x768.png)

The beauty of using a VM construct is that these vSphere Native Pods are isolated at the hypervisor layer. Unlike pods that run on the same Linux host which share the same Linux kernel and virtual hardware (CPU and memory). vSphere Native Pods have completely separate Linux Kernel and virtual hardware, hence much stronger isolation from security and resource consumption perspective. Simplifying security and ensuring proper isolation models for multi-tenancy.

## Modern IT Centers Around Flexibility

It's all about using the right tool for the job. The current focus of the industry is to reach cloud-native nirvana. However, cloud-native can be great for some products, while other applications benefit from a more monolith perspective. Most applications are a hybrid form of microservices mixed with stateful data collections. Project Pacific allows the customer to use the correct tool for the job; all managed and operated from a single platform.

## VMware Breakouts to Attend or Watch

[HBI4937BU - The future of vSphere: What you need to know now](https://my.vmworld.com/widget/vmware/vmworld19us/us19catalog?search=HBI4937BU) by Kit Colbert. Monday, August 26, 01:00 PM - 02:00 PM | Moscone West, Level 3, Room 3022

More to follow

## Where Can I Sign Up for a Beta?

We called this initiative a project as it is not tied to a particular release of vSphere. Because it's in tech preview, we do not have a beta program going on at the moment. As this project is a significant overhaul of the vSphere platform, we want to collect as much direct feedback from customers as we can. You can expect we will make much noise when the beta program of Project Pacific starts.

Stay tuned!
