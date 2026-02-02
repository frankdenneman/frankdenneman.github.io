---
title: "Disable DRS and VM-Host rules"
date: 2010-07-22
categories: 
  - "drs"
tags: 
  - "disable-drs"
  - "vm-host-affinity-rule"
  - "vmware"
---

vSphere 4.1 introduces [DRS VM-Host Affinity rules](http://frankdenneman.nl/2010/07/vm-to-hosts-affinity-rule/) and offer two types of rules, mandatory (must run on /must not run on) and preferential (should run on /should nor run on). When creating mandatory rules, all ESX hosts not contained in the specified ESX Host DRS Group are marked as “incompatible” hosts and DRS\\VMotion tasks will be rejected if an incompatible ESX Host is selected. A colleague of mine ran into the problem that mandatory VM-Host affinity rules remain active after disabling DRS; the product team explained the reason why: By design, mandatory rules are considered very important and it’s believed that the intended user case which is licensing compliance is so important, that VMware decided to apply these restrictions to non-DRS operations in the cluster as well. If DRS is disabled while mandatory VM-Host rules still exist, mandatory rules are still in effect and the cluster continues to track, report and alert mandatory rules. If a VMotion would violate the mandatory VM-Host affinity rule even after DRS is disabled, the cluster still rejects the VMotion. Mandatory rules can only be disabled if the administrator explicitly does so. If it the administrator intent to disable DRS, remove mandatory rules first before disabling DRS.
