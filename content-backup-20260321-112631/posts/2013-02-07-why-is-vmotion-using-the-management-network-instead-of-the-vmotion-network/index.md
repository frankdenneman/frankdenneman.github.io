---
title: "Why is vMotion using the management network instead of the vMotion network?"
date: 2013-02-07
categories: 
  - "vmotion"
---

On the community forums, I’ve seen some questions about the use of the management network by vMotion operations. The two most common scenarios are explained, please let me know if you notice this behavior in other scenarios.

**Scenario 1: Cross host and non-shared datastore migration** vSphere 5.1 provides the ability to migrate a virtual machine between [hosts and non-shared datastores simultaneously](http://frankdenneman.nl/2012/09/07/vsphere-5-1-vmotion-deepdive/ "vSphere 5.1 vMotion deepdive"). If the virtual machine is stored on a local or non-shared datastore vMotion is using the vMotion network to transfer the data to the destination datastore. When monitoring the VMkernel NICs, some traffic can be seen following over the management NIC instead of the VMkernel NIC enabled for vMotion. When migrating a virtual machine, vMotion determines hot data and cold data. Virtual disks or snapshots that are actively used are considered hot data, while the cold data are the underlying snapshots and base disk. Let’s use a virtual machine with 5 snapshots as an example. The active data is the recent snapshot, this is sent over across the vMotion network while the base disk and the 4 older snapshots are migrated via a network file copy operation across the first VMkernel NIC (vmk0).

The reason why vMotion uses separate networks is that the vMotion network is reserved for data migration of performance-related content. If the vMotion network is used for network file copies of cold data, it could saturate the network with non-performance related content and thereby starving traffic that is dependent on bandwidth. Please remember that everything sent over the vMotion network directly affects the performance of the migrating virtual machine.

During a vMotion the VMkernel mirrors the active I/O between the source and the destination host. If vMotion would pump the entire disk hierarchy across the vMotion network it would steal bandwidth from the I/O mirror process and this will hurt the performance of the virtual machine. If the virtual machine does not contain any snapshots, the VMDK is considered active and it is migrated across the vMotion network. The files in the VMDK directory are copied across the network of the first VMkernel NIC.

**Scenario 2: Management network and vMotion network sharing same IP-range/subnet** If the management network (actually the first VMkernel NIC) and the vMotion network share the same subnet (same IP-range) vMotion sends traffic across the network attached to first VMkernel NIC. It does not matter if you create a vMotion network on a different standard switch or distributed switch or assign different NICs to it, vMotion will default to the first VMkernel NIC if same IP-range/subnet is detected. Please be aware that this behavior is only applicable to traffic that is sent by the source host. The destination host receives incoming vMotion traffic on the vMotion network!

I’ve been conducting an online-poll and more than 95% of the respondents are using a dedicated IP-range for the vMotion traffic. Nevertheless, I would like to remind you that it’s recommended to use a separate network for vMotion. The management network is considered to be an unsecured network and therefore vMotion traffic should not be using this network. You might see this behavior in POC environments where you use a single IP-range for virtual infrastructure management traffic.

If the host is configured with a [Multi-NIC vMotion configuration](http://frankdenneman.nl/2012/12/18/designing-your-vmotion-network/ "Designing your vMotion network") using the same subnet as the management network/1st VMkernel NIC, then vMotion respects the vMotion configuration and only sends traffic through the vMotion-enabled VMkernel NICs.

If you have an environment that is using a single IP-range for the management network and the vMotion network, I would recommend creating a Multi-NIC vMotion configuration. If you have a limited amount of NICs, you can assign the same NIC to both VMkernel NICs, although you do not leverage the load balancing functionality, you force the VMkernel to use the vMotion-enabled networks exclusively.
