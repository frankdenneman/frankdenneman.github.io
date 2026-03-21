---
title: "vSphere 5.1 update 1 release fixes Storage vMotion rename &quot;bug&quot;"
date: 2013-04-26
categories: 
  - "vmotion"
  - "vmware"
---

vSphere 5.1 update 1 is released today which contains several updates and bug fixes for both ESXi and vCenter Server 5.1. This release contains the return of the much requested functionality of renaming VM files by using Storage vMotion. Renaming a virtual machine within vCenter did not automatically rename the files, but in previous versions Storage vMotion renamed the files and folder to match the virtual machine name. A nice trick to keep the file structure aligned with the vCenter inventory. However engineers considered it a bug and "fixed" the problem. Duncan and I pushed hard for this fix, but the strong voice of the community lead (thanks for all who submitted a [feature request](http://frankdenneman.nl/2012/11/12/vmware-feature-request/ "VMware feature request")) helped the engineers and product managers understand that this bug was actually considered to be a very useful feature. The engineers introduced the "bugfix" in [5.0 update 2](http://frankdenneman.nl/2013/01/21/storage-drs-cluster-shows-error-index-was-out-of-range-must-be-non-negative-and-less-than-the-size-of-the-collection-2/ "Storage DRS Cluster shows error ") end of last year and now the fix is included in this update for vSphere 5.1 Here's the details of the bugfix:

> vSphere 5 Storage vMotion is unable to rename virtual machine files on completing migration In vCenter Server , when you rename a virtual machine in the vSphere Client, the VMDK disks are not renamed following a successful Storage vMotion task. When you perform a Storage vMotion task for the virtual machine to have its folder and associated files renamed to match the new name, the virtual machine folder name changes, but the virtual machine file names do not change. This issue is resolved in this release. To enable this renaming feature, you need to configure the advanced settings in vCenter Server and set the value of the provisioning.relocate.enableRename parameter to true.

Read the rest of the [vCenter 5.1 update 1release notes](http://www.vmware.com/support/vsphere5/doc/vsphere-vcenter-server-51u1-release-notes.html "vCenter 5.1 update 1 release notes") and [ESXi 5.1 update 1 release notes](http://www.vmware.com/support/vsphere5/doc/vsphere-esxi-51u1-release-notes.html "ESXi 5.1 update 1 release notes") to discover other bugfixes
