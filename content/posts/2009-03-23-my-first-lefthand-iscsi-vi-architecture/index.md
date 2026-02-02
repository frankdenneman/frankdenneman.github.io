---
title: "My first lefthand ISCSI VI architecture"
date: 2009-03-23
categories: 
  - "storage"
tags: 
  - "esx"
  - "iscsi"
  - "lefthand"
---

I’m currently reviewing a design of a new virtual infrastructure. The VI uses multiple 10GB links to connect to a very large HP Lefthand san. I’m more a Fibre Channel guy, but I believe that this solution will smoke most mid-range FC-sans. I cannot wait to deploy the VI on the SAN. But I need to get used to some differences between ISCSI and fibre channel configurations. <!--more--> The “problem” or my latest challenge is creating a LUN provisioning scheme where multiple clusters can connect to all the LUNs when a disaster occurs and a cluster has failed. Lefthand present the LUNs as targets instead using the LUN ID as a unique identifier. I’m used to design a LUN ID scheme per cluster, this way if a cluster fails, the “destination” cluster can connect to the LUNs of the failed cluster with the same LUN ID as the original cluster. But when a (lefthand) LUN is presented to the ESX server, it will use a unique target ID instead of a unique LUN ID. (vmhba1:2:0) I have done some testing and discovered that the assigned target ID can differ from ESX server to ESX server. I’m curious if the target ID is used when creating the UUID of the VMFS datastore. And I'm especially interested in what will happen if multiple ESX hosts are going to communicate with the LUN when all the ESX hosts will use a different “path” Maybe there isn’t a problem at all and different targets will work well, but is seems that I need to stop thinking in FC solutions and get used to iscsi Lefthand “quirks”. I’ve read the field guide for VMware infrastructures, I googled on terms like “iscsi lun scheme’s” but I cannot seem to find any real-life scenario’s. Maybe my Google skills are pitiful at the moment, and maybe someone can shed some lights on this and how they solved this “problem”.
