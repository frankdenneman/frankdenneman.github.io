---
title: "Send F11 key to nested ESXi on Mac"
date: 2013-11-05
categories: 
  - "vmware"
---

I only use Mac at home, most of the time it's great sometimes it's not. For example when installing or configuring your remote lab. I have a windows server installed on a virtual machine that runs vCenter and the vSphere client.

When I'm installing a new nested ESXi server, I connect with a remote desktop session to the Windows machine and use the VMware vSphere client.

During the ESXi install process, it requires to press the F11 key to continue with the install process. However, F11 isn't mapped by the vSphere client automatically and there isn't a menu option in the vSphere client to send it to the client.

Fortunately, I found the combination, so I'm writing it down here as I'm bound to forget.

**Press FN-CMD-F11 to send the key to the install screen of ESXi.**

Happy installing!
