---
title: "Upgrading to SRM 4 and SSL certificates"
date: 2009-11-08
categories: 
  - "vmware"
tags: 
  - "srm"
  - "ssl-certifcates"
  - "subject-alternative-name"
---

Recently I started to work on a project implementing SRM 4. One of the project requirements is to use SSL certificates issued by a trusted CA.  When upgrading to SRM 4, we ran into a small problem. Because of a change in the vCenter authentication protocol, a new certificate that complies with the new certificate content rules must be obtained. The requirements changed of the “Subject Alternative Name”, the SSL certificate issued for SRM 1 environments use the FQDN of the vCenter server host. In SRM 4 environments, the Subject Alternative Name field must contain the FQDN of the SRM server. This value will be different for each member of the SRM server pair. We installed the SRM server on a separate server, but If you have installed SRM on the vCenter server, then you do not need to acquire a new certificate.
