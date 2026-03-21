---
title: "Removing orphaned Nexus DVS"
date: 2010-03-11
categories: 
  - "networking"
tags: 
  - "1000v"
  - "cisco"
  - "dvs"
  - "nexus"
  - "vsm"
---

During the test of the Cisco Nexus 1000V the customer deleted the VSM first without removing the DVS using commands from within the VSM, ending up with an orphaned DVS. One can directly delete the DVS from the DB, but there are bunch of rows in multiple tables that need to be deleted. This is risky and may render DB in some inconsistent state if an error is made while deleting any rows. Luckily there is a more elegant way to remove an orphaned DVS without hacking and possibly breaking the vCenter DB. **A little background first:** When installing the Cisco Nexus 1000V VSM, the VSM uses an extension-key for identification. During the configuration process the VSM spawns a DVS and will configure it with the same extension-key. Due to the matching extension keys (extension session) the VSM owns the DVS essentially. And only the VSM with the same extension-key as the DVS can delete the DVS. So to be able to delete a DVS, a VSM must exist registered with the same extension key. If you deleted the VSM and are stuck with an orphaned DVS, the first thing to do is to install and configure a new VSM. Use a different switch name than the first (deleted) VSM. The new VSM will spawn a new DVS matching the switch name configured within the VSM. The first step is to remove the new spawned DVS and do this the proper way using commands from within the VSM virtual machine. <!--more-->**Removing DVS with Nexus VSM virtual machine:** Log in VSM Ping the vCenter to make sure you have a connection.

```
conf t
```

```
svs connection connection_name
```

The _connection\_name_ is created during the configuration of the connection between the VSM and the vCenter server. The default connection name is vCenter. To query the current connection name:

```
show svs connections
```

If the SVS connection output does not show a datacenter name, but the minus (-) sign, you must specify the vCenter datacenter where the DVS is created, with the following command: (In my case I needed to specify the datacenter even when the datacenter name was listed in the svs connection)

```
vmware dvs datacenter-name name (case sensitive)
```

e.g: vCenter datacenter name = DATACenter

```
vmware dvs datacenter-name DATACenter
```

Use the following command to remove the DVS:

```
no vmware dvs
```

The following warning appears:

```
This will remove the DVS from the vCenter Server and any associated port-groups
```

```
Do you really want to proceed (yes/no)
```

When selecting Yes, the following output appears in the VSM command prompt:

```
Note: Command execution in progress, please wait..
```

Simultaneously the recent task window in vCenter shows two tasks: Delete folder Delete vNetwork Distributed Switch Select Network Inventory view to check if the DVS is deleted. **Removing DVS after destroying the VSM virtual machine.** The first part was the easy part, removing a DVS after the corresponding VSM is removed is a bit trickier. First we must change the hostname of the VSM to reflect the switch name of the orphaned DVS. Log in VSM

```
conf t
hostname
exit
copy run start
```

After setting the new hostname, the command prompt changes immediately to the "new" hostname. At this moment, the VSM is using the same switch name, but it still uses a different extension-key as the orphaned DVS. We need to change the extension key of the VSM to match the extension key of the orphaned DVS. Both old and new extension keys are listed in the vCenter database. First we need to know which extension-key the VSM is currently using. This key is going to be deleted from the vCenter DB. This is done by using the following command in the VSM:

```
show vmware vc extension-key
```

The command prompt returns with an extension-key e.g:

```
Cisco_Nexus_1000V_1234101238
```

We need to remove this extension key from the vCenter DB, to do this we are going to use the managed Object Browser or (MOB. The Managed Object Browser is a web-based tool for working with the API. This tool enables you to browse managed objects on vCenter Server. Open an Internet Explorer window to access the vCenters’ MOB. Enter https:///mob See [KB 568529](http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=568529) for more information about using the Managed Object Browser operations. Log in with user with administrator rights in vCenter. Before we are going to unregister the “new” extension-key, we need to know which extension-key the old VSM used. (the values listed in italic are examples, the values in your environment can be different) Go to: ServiceContent: content rootFolder: _group-d8_ childEntity: _datacenter-76_ networkFolder: _group-n15_ childEntity: _group-n3456_ childEntity: _dvs-3457_ DVSConfigInfo: config At this moment, two keys exists, one key matching the orphaned DVS and one used by the newly spawned DVS during configuration of the second VSM. Copy the old key matching the orphaned DVS to notepad file; we are using that key later on. Now copy the key matching the new DVS, this key must be removed using the ExtensionManager. For example: extensionKey: "Cisco\_Nexus\_1000V\_1234101238” Go to: https://vcenterhostname/mob/?moid=ExtensionManager or follow the following path from the MOB home screen: ServiceContent: content extensionManger: ExtensionManager void: unregisterExtension extensionKey (required) string: paste key you copied from the DVSConfigInfo for example: extensionKey (required) string: Cisco\_Nexus\_1000V\_8321457891 Click on InvokeMethod This will return with the status: Method invocation result: void Now return to the VSM command prompt and use the old extension id of the first VSM (saved in notepad file).

```
vmware vc extension-key
```

If the following error appears:

```
Cannot change the extension key while a connection is already enabled
```

the svs connection is still active and you must disconnect the current SVS connection by entering the following commands:

```
svs connection vcenter
no connect
```

Issue the vmware vc extension-key again after closing the svs connection. At this point the VSM is configured with a matching extension-key as the orphaned DVS, but the VSM must registered within vCenter with this extension-key. To do this, you must use the extension.xml of the VSM, which is available for download on the webpage of the Nexus VSM. (Before I downloaded the xml file I restarted the vCenter, don’t know if this is necessary, but I just wanted to be sure that the prior configuration settings are saved and committed to the database.) **Register the VSM by importing the xml with the extension key of the orphaned DVS switch:** open internet explorer and enter the ip-address of the VSM. right click the link to save the cisco\_nexus\_1000v\_extension.xml to your computer open vcenter Select Plug-ins Manage Plug-ins... Right click on whitespace inside Plug-in Manager and select the option New Plug-in... click the Browse button and select the saved xml file click on Ok. now the Cisco\_Nexus\_1000v\_old extension key code appears in Available Plug-ins section. At this point the VSM is using the matching switch name and extension key of the orphaned DVS and is registered with the extension key in vCenter.Time to connect the VSM to vCenter. This will spawn a new DVS, this DVS will use the same extension key and switch name as the orphaned DVS and override all the info in the vCenter database. But because a extension session will exist we can remove the newly spawned DVS from the VSM using the commands mentioned in the first part of this article. Return to the command prompt of the VSM and issue the following commands;

```
conf t
svs connection vcenter
vmware dvs datacenter_name datacenter

```

The DVS is created with the same name as the orphaned dvs and overwriting the old configuration. When this is completed check the network inventory view. return to command promt and issue the command

```
no vmware dvs
```

to remove the new-old DVS. If you will receive an error follow the steps mentioned in the **Removing DVS with Nexus VSM virtual machine section**. The orphaned DVS is removed. More information about the Nexus commands go visit the [online nexus command reference](http://www.cisco.com/en/US/docs/switches/datacenter/nexus1000/sw/4_0/command/reference/n1000v_cmd_ref.html)
