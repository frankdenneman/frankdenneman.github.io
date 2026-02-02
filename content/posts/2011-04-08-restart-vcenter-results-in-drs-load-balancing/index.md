---
title: "Restart vCenter results in DRS load balancing"
date: 2011-04-08
categories: 
  - "drs"
---

Recently I had to troubleshoot an environment which appeared to have a DRS load-balancing problem. Every time when a host was brought out of maintenance mode, DRS didn’t migrate virtual machines to the empty host. Eventually virtual machines were migrated to the empty host but this happened after a couple of hours had passed. But after a restart of vCenter, DRS immediately started migrating virtual machines to the empty host. Restarting vCenter removes the cached historical information of the vMotion impact. vMotion impact information is a part of the Cost-Benefit Risk analysis. DRS uses this Cost-Benefit Metric to determine the return on investment of a migration. By comparing the cost, benefit and risks of each migration, DRS tries to avoid migrations with insufficient improvement on the load balance of the cluster. When removing the historical information a big part of the cost segment is lost, leading to a more positive ROI calculation, which in turn results in a more “aggressive” load-balance operation.
