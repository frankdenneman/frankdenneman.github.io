---
title: "Storage DRS enables SIOC on datastores only if I/O load balancing is enabled"
date: 2012-08-01
categories: 
  - "sioc"
  - "sdrs"
---

Lately, I've received some comments why I don't include SIOC in my articles when talking about space load balancing. Well, Storage DRS only enables SIOC on each datastore inside the datastore cluster if I/O load balancing is enabled. When you don’t enable I/O load balancing during the initial setup of the datastore cluster, SIOC is left disabled. Keep in mind when I/O load balancing is enabled on the datastore cluster and you disable the I/O load balancing feature, SIOC remains enabled on all datastores within the cluster.
