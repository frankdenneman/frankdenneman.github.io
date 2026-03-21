---
title: "Apply User-defined Storage Capabilities to multiple datastore at once"
date: 2012-10-01
categories: 
  - "sdrs"
tags: 
  - "assign-multiple-user-defined-storage-capabilities"
  - "storage-profiles"
---

To get a datastore cluster to surface a (user-defined) storage capability, all datastores inside the datastore cluster must be configured with the same storage capability. [![](images/00-Datastore-Cluster-view.png "00-Datastore Cluster view")](http://frankdenneman.nl/wp-content/uploads/2012/10/00-Datastore-Cluster-view.png) When creating Storage Capabilities, the UI does not contain a view where to associate a storage capability with multiple datastores. However that does not mean the web client does not provide you with the ability to do so. Just use the multi-select function of the webclient. Go to Storage, select the datastore cluster, select Related Objects and go to Datastores view. To select all datastores, click the first datastore, hold shift and select the last datastore. Right click and select assign storage capabilities. [![](images/01-perform-this-action.png "01-perform-this-action")](http://frankdenneman.nl/wp-content/uploads/2012/10/01-perform-this-action.png) Select the appropriate Storage capability and click on OK. [![](images/02-assign.png "02-assign")](http://frankdenneman.nl/wp-content/uploads/2012/10/02-assign.png) The Datastore Cluster summary tab now shows the user-defined Storage Capability. [![](images/03-surfaced-storage-capability.png "03-surfaced-storage-capability")](http://frankdenneman.nl/wp-content/uploads/2012/10/03-surfaced-storage-capability.png) Get notification of these blogs postings and more DRS and Storage DRS information by following me on Twitter: [@frankdenneman](https://twitter.com/FrankDenneman)
