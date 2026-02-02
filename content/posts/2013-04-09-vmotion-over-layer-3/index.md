---
title: "vMotion over layer 3?"
date: 2013-04-09
categories: 
  - "vmotion"
---

This question regularly pops up on twitter and the community forums. And yes it works but VMware does not support vMotion interfaces in different subnets. The reason is that this can break functionality in higher-level features that rely on vMotion to work. If you think Routed vMotion (vMotion interfaces in different subnets) is something that should be available in the modern datacenter, please fill out a [feature request](http://frankdenneman.nl/2012/11/12/vmware-feature-request/ "VMware feature request"). The more feature requests we receive; the more priority can be applied to the development process of the feature.
