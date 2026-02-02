---
title: "FDM in mixed ESX and vSphere clusters"
date: 2011-10-17
categories: 
  - "vmware"
tags: 
  - "fdm"
  - "ha"
  - "mixed-clusters"
---

Last couple of weeks I’ve been receiving questions about vSphere HA FDM agent in a mixed cluster. When upgrading vCenter to 5.0, each HA cluster will be upgraded to the FDM agent. A new FDM agent will be pushed to each ESX server. The new HA version supports ESX(i) 3.5 through ESXi 5.0 hosts. Mixed clusters will be supported so not all hosts have to be upgraded immediately to take advantage of the new features of FDM. Although mixed environments are supported we do recommend keeping the time you run difference versions in a cluster to a minimum. The FDM agent will be pushed to each hosts, even if the cluster contains identically configured hosts, for example a cluster containing only vSphere 4.1 update 1 will still be upgraded to the new HA version. The only time vCenter will not push the new FDM agent to a host if the host in question is a 3.5 host without the required patch. When using clusters containing 3.5 hosts, it is recommended to upgrade the ESX host to ESX350-201012401-SG PATCH (ESX 3.5) or ESXe350-201012401-I-BG PATCH (ESXi) patch first before upgrading vCenter to vCenter 5.0. If you still get the following error message: _Host '' is of type ( ) with build , it does not support vSphere HA clustering features and cannot be part of vSphere HA clusters._ Visit the VMware knowledgebase article: [2001833]( http://kb.vmware.com/kb/2001833).
