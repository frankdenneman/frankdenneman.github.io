---
title: "Storage DRS and Storage vMotion bugs solved in vSphere 5.0 Update 2."
date: 2012-12-21
categories: 
  - "sdrs"
  - "vmotion"
  - "vmware"
---

Today Update 2 for vSphere ESXI 5.0 and vCenter Server 5.0 were released. I would like to highlight two bugs that have been fixed in this update, one for Storage DRS and one for Storage vMotion **Storage DRS** vSphere ESXi 5.0 Update 2 was released today and it contains a fix that should be interesting to customers running Storage DRS on vSphere 5.0. The release note states the following bug:

> Adding a new hard disk to a virtual machine that resides on a Storage DRS enabled datastore cluster might result in Insufficient Disk Space error When you add a virtual disk to a virtual machine that resides on a Storage DRS enabled datastore and if the size of the virtual disk is greater than the free space available in the datastore, SDRS might migrate another virtual machine out of the datastore to allow sufficient free space for adding the virtual disk. Storage vMotion operation completes but the subsequent addition of virtual disk to the virtual machine might fail and an error message similar to the following might be displayed: Insufficient Disk Space

In essence Storage DRS made room for the incoming virtual machine, but failed to place the new virtual machine. This update fixes a bug in the datastore cluster defragmentation process. For more information about datastore cluster defragmentation read the article: [Storage DRS initial placement and datastore cluster defragmentation](http://frankdenneman.nl/sdrs/storage-drs-initial-placement-and-datastore-cluster-defragmentation/). **Storage vMotion** vCenter Server 5.0 Update 2 contains a fix that allows you to rename your virtual machine files with a Storage vMotion.

> vSphere 5 Storage vMotion is unable to rename virtual machine files on completing migration In vCenter Server , when you rename a virtual machine in the vSphere Client, the vmdk disks are not renamed following a successful Storage vMotion task. When you perform a Storage vMotion of the virtual machine to have its folder and associated files renamed to match the new name. The virtual machine folder name changes, but the virtual machine file names do not change.

Duncan and I knew how many customers where relying on this feature for operational processes and pushed heavily to get it back in. We are very pleased to announce it’s back in vSphere 5.0, **unfortunately this fix is not available in 5.1 yet**! For more info about the fixes in the updates please review the release notes: **ESXi 5.0 :** [https://www.vmware.com/support/vsphere5/doc/vsp\_esxi50\_u2\_rel\_notes.html](https://www.vmware.com/support/vsphere5/doc/vsp_esxi50_u2_rel_notes.html) **vCenter 5.0:** [https://www.vmware.com/support/vsphere5/doc/vsp\_vc50\_u2\_rel\_notes.html](https://www.vmware.com/support/vsphere5/doc/vsp_vc50_u2_rel_notes.html)
