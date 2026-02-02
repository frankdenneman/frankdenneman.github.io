---
title: "Storage DRS Cluster shows error &#034;Index was out of range. Must be non-negative and less than the size of the collection."
date: 2013-01-21
categories: 
  - "sdrs"
---

Recently I have noticed an increase of tweets mentioning the error “Index was out of range” **Error message:** When trying to edit the settings of a storage DRS cluster, or when clicking on SDRS scheduling settings an error pops up:

> "An internal error occurred in the vSphere Client. Details: Index was out of range. Must be non-negative and less than the size of the collection. Parameter name: index"

**Impact:** This error does not have any impact on Storage DRS operations and/or Storage DRS functionality and is considered a “cosmetic” issue. See KB article: [KB 2009765](http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=2009765 "KB 2009765"). **Solution:** [VMware vCenter Server 5.0 Update 2](https://www.vmware.com/support/vsphere5/doc/vsp_vc50_u2_rel_notes.html "VMware vCenter Server 5.0 Update 2 release notes") fixes this problem. Apply Update 2 if you experience this error. As the fix is included in the Update 2 for vCenter 5.0, I expect that vCenter 5.1 Update 1 will include the fix as well, however I cannot confirm any deliverables.
