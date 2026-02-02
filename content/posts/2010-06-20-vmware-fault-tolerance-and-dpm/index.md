---
title: "VMware Fault Tolerance and DPM"
date: 2010-06-20
categories: 
  - "drs"
tags: 
  - "dpm"
  - "fault-tolerance"
  - "vmware"
---

Some requirements of the design I am working on is to be as “green” as possible and to offer the highest level of redundancy for business continuity. Enter VMware Fault Tolerance (FT) and Distributed Power Management (DPM)! When mixing multiple features, the requirements of one feature can have impact on- or even worse becomes a constraint of the other feature. DPM works together with DRS to VMotion virtual machines onto fewer ESX host servers when the resource demand drops below a specific threshold. In the current release of vSphere, DRS does not consider the FT-enabled virtual machines during load balancing operations and DRS will not migrate FT-enabled virtual machine automatically, because of this DPM cannot power down these hosts until the administrator will manually VMotion the primary or secondary virtual machines to another ESX host server. Fortunately when enabling DPM on the cluster, you can disable DPM at ESX host level. Due to the current limitations of DRS with VMware Fault Tolerance, it is recommended to disable DPM on at least two ESX server host to act as host for FT-enabled virtual machines.
