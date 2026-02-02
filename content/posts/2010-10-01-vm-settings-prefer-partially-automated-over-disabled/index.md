---
title: "VM settings: Prefer Partially Automated over Disabled"
date: 2010-10-01
categories: 
  - "drs"
tags: 
  - "drs"
  - "partially-automated"
  - "vmware"
---

Due to requirements or constraints it might be necessary to exclude a virtual machine from automatic migration and stop it from moving around by DRS. Use the “Partially automated” setting instead of “Disabled” at the individual virtual machine automation level. Partially automated blocks automated migration by DRS, but keep the initial placement function. During startup, DRS is still able to select the most optimal host for the virtual machine. By selecting the “Disabled” function, the virtual machine is started on the ESX server it is registered and chances of getting an optimal placement are low(er). An exception for this recommendation might be a virtualized vCenter server, most admins like to keep track of the vCenter server in case a disaster happens. After a disaster occurs, for example a datacenter-wide power-outage, they only need to power-up the ESX host on which the vCenter VM is registered and manually power-up the vCenter VM. An alternative to this method is to keep track of the datastore vCenter is placed on and register and power-on the VM on a (random) ESX host after a disaster. Slightly more work than disabling DRS for vCenter, but offers probably better performance of the vCenter Virtual Machine during normal operations. Due to expanding virtual infrastructures and new additional features, vCenter is becoming more and more important for day-to-day operational management today. Assuring good performance outweighs any additional effort necessary after a (hopefully) rare occasion, but both methods have merits.
