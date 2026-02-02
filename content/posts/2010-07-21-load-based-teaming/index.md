---
title: "Load Based Teaming"
date: 2010-07-21
categories: 
  - "networking"
tags: 
  - "lbt"
  - "vmware"
---

In vSphere 4.1 a new network Load Based Teaming (LBT) algorithm is available on the distributed virtual switch dvPort groups. The option “_Route based on physical NIC load_” takes the virtual machine network I/O load into account and tries to avoid congestion by dynamically reassigning and balancing the virtual switch port to physical NIC mappings. The three existing load-balancing policies, Port-ID, Mac-Based and IP-hash use a static mapping between virtual switch ports and the connected uplinks. The VMkernel assigns a virtual switch port during the power-on of a virtual machine, this virtual switch port gets assigned to a physical NIC based on either a round-robin- or hashing algorithm, but all algorithms do not take overall utilization of the pNIC into account. This can lead to a scenario where several virtual machines mapped to the same physical adapter saturate the physical NIC and fight for bandwidth while the other adapters are underutilized. LBT solves this by remapping the virtual switch ports to a physical NIC when congestion is detected. After the initial virtual switch port to physical port assignment is completed, Load Based teaming checks the load on the dvUplinks at a 30 second interval and dynamically reassigns port bindings based on the current network load and the level of saturation of the dvUplinks. The VMkernel indicates the network I/O load as congested if transmit (Tx) or receive (Rx) network traffic is exceeding a 75% mean over a 30 second period. (The mean is the sum of the observations divided by the number of observations). An interval period of 30 seconds is used to avoid MAC address flapping issues with the physical switches. Although an interval of 30 seconds is used, it is recommended to enable port fast (trunk fast) on the physical switches, all switches must be a part of the same layer 2 domain.
