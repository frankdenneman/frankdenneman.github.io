---
title: "DRS 4.1 Adaptive MaxMovesPerHost"
date: 2010-08-27
categories: 
  - "drs"
tags: 
  - "drs"
  - "maxmovesperhost"
  - "vmware"
---

Another reason to upgrade to vSphere 4.1 is the DRS adaptive MaxMovesPerHost parameter. The MaxMovesPerHost setting determines the maximum amount of migrations per host for DRS load balancing. DRS evaluates a cluster and recommends migrations. By default this evaluation happens every 5 minutes. There are limits to how many migrations DRS will recommend per interval per ESX host because there's no advantage to recommending so many migrations that they won't all be completed by the next re-evaluation, by which time demand could have changed anyway. Be aware that there is no limit on max moves per host for a host entering maintenance or standby mode, but there's a limit on max moves per host for load balancing. This can (**but usually shouldn't**) be changed by setting the DRS Advanced Option "MaxMovesPerHost". The default value is 8 and is set at the Cluster level. Remember, the MaxMovesPerHost is a cluster setting but configures the maximum migrations from a single host on each DRS invocation. This means you can still see 30 or 40 vMotion operations in the cluster during a DRS invocation. In ESX/ESXi 4.1, the limit on moves per host will be dynamic, based on how many moves DRS thinks can be completed in one DRS evaluation interval. DRS adapts to the frequency it is invoked (pollPeriodSec, default 300 seconds) and the average migration time observed from previous migrations. In addition DRS follows the new maximum number of concurrent vMotion operations per host over depending on the Network Speed (1GB – 4 vMotions, 10GB – 8 vMotions). Due to the adaptive nature the algorithm, the name of the setting is quite misleading as it's no longer a maximum. The "MaxMovesPerHost" parameter will still exist, but its value might be exceeded by DRS. By leveraging the increased amount of concurrent vMotion operations per host and the evaluation of previous migration times DRS is able to rebalance the cluster in a fewer amount of passes. By using fewer amounts of passes, the virtual machines will receive their entitled resources much quicker which should positively affect virtual machine performance.
