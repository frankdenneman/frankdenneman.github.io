---
title: "Adjust timeout value ESXi Embedded Host Client"
date: 2016-04-12
categories: 
  - "vmware"
---

I love to use the ESXi Embedded Host Client next to vCenter in my lab. It's quick, it provide most of the functionality and best of it all it has a functioning VM console when accessing it from a MAC. The ESXi Embedded Host Client time-out default is set to 15 minutes, but you can adjust this setting. [![Time-out ESXI embedded client](images/Time-out-ESXI-embedded-client.png)](http://frankdenneman.nl/wp-content/uploads/2016/04/Time-out-ESXI-embedded-client.png) On the right side of the menu bar there is a drop down menu next to the IP-address or DNS name of your ESXi server. Open it and go to:

1. Settings
2. Application timeout
3. Select the appropriate timeout value

As I use it in my lab, I select the option off, but if you use this in other environments I can expect you use a different value.
