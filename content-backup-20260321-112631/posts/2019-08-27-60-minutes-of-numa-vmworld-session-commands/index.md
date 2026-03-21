---
title: "60 Minutes of NUMA VMworld Session Commands"
date: 2019-08-27
categories: 
  - "numa"
coverImage: "Screenshot-2019-08-27-12.21.00.png"
---

## Verify Distribution of Memory Modules with PowerCLI

```
Get-CimInstance -CimSession $Session CIM_PhysicalMemory | select BankLabel, Description, @{n=‘Capacity in GB';e={$_.Capacity/1GB}}  
```

## PowerCLI Script to Detect Node Interleaving

```
Get-VMhost | select @{Name="Host Name";Expression={$_.Name}}, ​@{Name="CPU Sockets";Expression={$_.ExtensionData.Hardware.CpuInfo.NumCpuPackages}}, ​@{Name="NUMA Nodes";Expression={$_.ExtensionData.Hardware.NumaInfo.NumNodes}} 
```

## Action-Affinity Monitoring

```
Sched-Stats
-t numa-migration 
```

## Disable Action Affinity

```
numa.LocalityWeightActionAffinity = 0  
```

## numa.PreferHT

For more information on how to enable PreferHT: KB article 2003582

```
Host Setting:  numa.PreferHT=1  
```

```
VM Setting:  numa.vcpu.PreferHT = TRUE 
```
