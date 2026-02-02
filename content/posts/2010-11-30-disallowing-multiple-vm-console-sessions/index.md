---
title: "Disallowing multiple vm console sessions"
date: 2010-11-30
categories: 
  - "vmware"
tags: 
  - "restrict-vm-console"
  - "security"
---

Currently I’m involved in a high-secure virtual infrastructure design and we are required to reduce the number of entry points to the virtual infrastructure. One of the requirements is to allow only a single session to the virtual machine console. Due to the increasing awareness \\ demand of security in virtual infrastructure more organizations might want to apply this security setting. 1. Turn of the virtual machine. 2. Open Configuration parameters of the VM to edit the advanced configuration settings 3. Add Remote.Display.maxConnections with a value of 1 4. Power on virtual machine **Update**: Arne Fokkema created a Power-CLI function to automate configuring this setting throughout your virtual infrastructure. You can find the power-cli function on [ICT-freak.nl](http://ict-freak.nl/2010/11/30/powercli-re-disallowing-multiple-vm-console-sessions/).
