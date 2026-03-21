---
title: "(Storage) DRS (anti-) affinity rule types and HA interoperability"
date: 2012-02-06
categories: 
  - "drs"
  - "sdrs"
---

Lately I have received many questions about the interoperability between HA and affinity rules of DRS and Storage DRS. I’ve created a table listing the (anti-) affinity rules available in a vSphere 5.0 environment.

| **Technology** | **Type** | **Affinity** | **Anti-Affinity** | **Respected by VMware HA** |
| --- | --- | --- | --- | --- |
| DRS | VM-VM | Keep virtual machines together | Separate virtual machines | No |
| VM-Host | Should run on hosts in group | Should not run on hosts in group | No |
| Must run on hosts in group | Must not run on hosts in group | **Yes** |
|  |  |  |  |  |
| SDRS | Intra-VM | VMDK affinity | VMDK anti-affinity | N/A |
| VM-VM | Not available | VM Anti-Affinity | N/A |

As the table shows, HA will ignore most of the (anti-) affinity rules in its placement operations after a host failure except the “Virtual Machine to Host - Must rules”. Every type of rule is part of the DRS ecosystem and exists in the vCenter database only. A restart of a virtual machine performed by HA is a host-level operation and HA does not consult the vCenter database before powering-on a virtual machine. **Virtual machine compatibility list** The reason why HA respect the "must-rules" is because of DRS's interaction with the host-local “compatlist” file. This file contains a compatibility info matrix for every HA protected virtual machine and lists all the hosts with which the virtual machine is compatible. This means that HA will only restart a virtual machine on hosts listed in the compatlist file. **DRS Virtual machine to host rule** A “virtual machine to hosts” rule requires the creation of a Host DRS Group, this cluster host group is usually a subset of hosts that are member of the HA and DRS cluster. Because of the intended use-case for must-rules, such as honoring ISV licensing models, the cluster host group associated with a must-rule is directly pushed down in the compatlist. **Note** Please be aware that the compatibility list file is used by all types of power-on operations and load-balancing operations. When a virtual machine is powered-on, whether manual (admin) or by HA, the compatibility list is checked. When DRS performs a load-balancing operation or maintenance mode operation, it checks the compatibility list. This means that no type of operation can override must- type affinity rules. For more information about when to use must and should rules, please read this article: [Should or Must VM-Host affinity rules](http://frankdenneman.nl/2010/12/vm-host-affinity-rules-should-or-must/ "Should or Must VM-Host affinity rules"). **Contraint violations** After HA powers-on a virtual machine, it might violate any VM-VM or VM-host should (anti-) affinity rule. DRS will correct this constraint violation in the first following invocation and restore “peace” to the cluster. **Storage DRS (anti-) affinity rules** When HA restarts a virtual machine, it will not move the virtual machine files. Therefore creation of Storage DRS (anti-) affinity rules do not affect virtual machine placement after a host failure.
