---
title: "Simulating NUMA Nodes for Nested ESXi Virtual Appliances"
date: 2023-03-02
categories: 
  - "numa"
tags: 
  - "vmware"
coverImage: "Host-Config-Hardware-Overview.png"
---

To troubleshoot a particular NUMA client behavior in a heterogeneous multi-cloud environment, I needed to set up an ESXi 7.0 environment. Currently, my lab is running ESXi 8.0, so I've turned to William Lams' excellent repository of nested ESXi virtual appliances and downloaded a copy of the 7.0 u3k version.

My physical ESXi hosts are equipped with Intel Xeon Gold 5218R CPUs, containing 20 cores per socket. The smallest ESXi host contains ten cores per socket in the environment I need to simulate. Therefore, I created a virtual ESXi host with 20 vCPUs and ensured that there were two virtual sockets (10 cores per socket)

![](images/10-Cores-per-Socket-1024x397.png)

Once everything was set up and the ESXi host was operational, I checked to see if I could deploy a 16 vCPU VM to simulate particular NUMA client configuration behavior and verify the CPU environment.  
The first command I use is to check the "physical" NUMA node configuration "`sched-stats -t numa-node`". But this command does not give me any output, which should not happen.

![](images/sched-stats-t-numa-pnode-no-output.png)

Let's investigate, let's start off by querying the CPUinfo of the VMkernel Sys Info Shell (vsish): `vsish -e get /hardware/cpu/cpuInfo`

![](images/vsish-cpuinfo.png)

The ESXi host contains two CPU packages. The VM configuration Cores per Socket has provided the correct information to the ESXi kernel. The same info can be seen in the UI at Host Configuration, Hardware, Overview, and Processor.

![](images/Host-Config-Hardware-Overview.png)

However, it doesn't indicate the number of NUMA nodes supported by the ESXi kernel. You would expect that two CPU packages would correspond to at least two NUMA nodes. The command  
`vsish -e dir /hardware/cpuTopology/numa/nodes` shows the number of NUMA nodes that the ESXi kernel detects

![](images/vsish-numa-node.png)

It only detects 1 NUMA node as the virtual NUMA client configuration has been decoupled from the Cores Per Socket configuration since ESXi 6.5. As a result, the VM is presented by the physical ESXi host as a single virtual NUMA node, and the virtual ESXi host picks this up. Logging in to the physical host, we can validate the nested ESXi VM configuration and run the following command.

`vmdumper -l | cut -d \/ -f 2-5 | while read path; do egrep -oi "DICT._(displayname._|numa._|cores._|vcpu._|memsize._|affinity._)= ._|numa:._|numaHost:._" "/$path/vmware.log"; echo -e; done`

![](images/NUMA-vmdumper.png)

The screen dump shows that the VM is configured with one Virtual Proximity Domain (VPD) and one Physical Proximity Domain (PPD). The VPD is the NUMA client element that is exposed to the VM as the virtual NUMA topology, and the screenshot shows that all the vCPUs (0-19) are part of a single NUMA client. The NUMA scheduler uses the PPD to group and place the vCPUs on a specific NUMA domain (CPU package).

By default, the NUMA scheduler consolidates vCPUs of a single VM into a single NUMA client up to the same number of physical cores in a CPU package. In this example, that is 20. As my physical ESXi host contains 20 CPU cores per CPU package, all the vCPUs in my nested ESXi virtual appliance are placed in a single NUMA client and scheduled on a single physical NUMA node as this will provide the best possible performance for the VM, regardless of the Cores per Socket setting.

The VM advanced configuration parameter `numa.consolidate = "false`" forces the NUMA scheduler to evenly distribute the vCPU across the available physical NUMA nodes.

![](images/numa.consolidatefalse-1024x372.png)

After running the vmdumper instruction once more, you see that the NUMA configuration has changed. The vCPUs are now evenly distributed across two PPDs, but only one VPD exists. This is done on purpose, as we typically do not want to change the CPU configuration for the guest OS and application, as that can interfere with previously made optimizations.

![](images/NUMA-vmdumper-2-ppd-1-vpd.png)

You can do two things to change the configuration of the VPD, use the VM advanced configuration parameter `numa.vcpu.maxPerVirtualNode` and set it to `10`. Or remove the `numa.autosize.vcpu.maxPerVirtualNode` = "20" from the VMX file.

![](images/image-vmx-file.png)

I prefer removing the `numa.autosize.vcpu.maxPerVirtualNode` setting, as this automatically follows the PPD configuration, it avoids mismatches between `numa.vcpu.maxPerVirtualNode` and the automatic `numa.consolidate = "false"` configuration. Plus, it's one less advanced setting in the VMX, but that's just splitting hairs. After powering up the nested ESXi virtual appliance, you can verify the NUMA configuration once more in the physical ESXi host:

![](images/Image-vmdumper-2-ppd-2-ppd.png)

The vsish command `vsish -e dir /hardware/cpuTopology/numa/nodes` shows ESXi detects two NUMA nodes

![](images/vsish-2-NUMA-nodes.png)

and `sched-stats -t numa-pnode` now returns the information you expect to see

![](images/sched-stats-t-numa-pnode-output.png)

Please note that if the vCPU count of the nested ESXi virtual appliance exceeds the CPU core count of the CPU package, the NUMA scheduler automatically creates multiple NUMA clients.
