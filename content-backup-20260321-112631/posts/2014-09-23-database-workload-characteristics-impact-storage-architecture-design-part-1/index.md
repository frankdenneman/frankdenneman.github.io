---
title: "Database workload characteristics and their impact on storage architecture design - part 1"
date: 2014-09-23
categories: 
  - "miscellaneous"
---

Frequently PernixData FVP is used to accelerate databases. Databases are for many a black box solution. Sure we all know they consume resources like there is no tomorrow, but can we make some general statements about database resource consumption from a storage technology perspective? I asked Bala Narasimhan, our director of Products, a couple of questions to get a better understanding about the database operations and how FVP can help to provide the performance the business needs. [![Bala](images/Bala.jpeg)](http://frankdenneman.nl/wp-content/uploads/2014/09/Bala.jpeg)The reason why I asked Bala about databases is because of his rich background in database technology. After spending some time at HP writing kernel memory management software, he moved to Oracle and was responsible for memory SGA and PGA. One of his proudest achievements was to build the automatic memory management in 10G. He then went on and worked at a startup where he rewrote the open source database, Postgres, to be a scale out, columnar relational databases for data warehousing and analytics. Bala recently recorded a [webinar eliminate performance bottlenecks in virtualized Databases](http://info.pernixdata.com/Eliminate-Performance-Bottlenecks "Eliminate Performance Bottlenecks in Virtualized Databases"). Bala’s twitter account can be found [here](https://twitter.com/BalaNarasimhan "Bala on twitter"). As the topic databases is an extensive one, the article is split up into a series of smaller articles, making it more digestible.

###### Question 1: What are the various databases use cases one typically sees?

There is a spectrum of use cases, with OLTP, Reporting, OLAP and analytics being the common ones. Reporting, OLAP (online analytical processing) and Analytics can be seen as a part of the data warehousing family. OLTP (online transaction processing) databases are typically aligned with a single application and acts as an input source for data warehouses. Therefore a data warehouse can be seen as a layer on top of the OLTP database optimized for reporting and analytics. When you deal with setting up architectures for databases you have to ask yourself, what do you try to solve? What is technical requirement of the workload? Is it latency intensive, do you retrieve or do you want to read a lot of data as fast as possible? Is the application latency sensitive or throughput bound? Meaning that if you go from left to right in the table on average the block size grows. Hint: the larger the block size means that on average you are dealing with a more throughput bound workload instead of a latency sensitive block size. From left to right the database design go from normalized to denormalized.

|  | OLTP | Reporting | OLAP | Analytics |
| --- | --- | --- | --- | --- |

###### Database Schema Design

OLTP is an excellent example of a normalized schema. A database schema can be seen as a container objects and allows to logically group objects such as tables, views and stored procedures. When using a normalized schema you start to split a table into smaller tables. For example, lets assume a bank database has only one table that logs all activities by all its customers. This means that there are multiple rows in this table for each customer. Now if a customer updates her address you need to update many rows in the database for the database to be consistent. This can have a impact on the performance and concurrency of the database. Instead of this, you could build out a schema for the database such that there are multiple tables and there is only one table that has customer details in it. This way when the customer changes her address you only need to update one row in this table and this improves concurrency and performance If you normalize your database enough every insert, delete and update statement will only hit a single table, very small updates that require fast responds, therefor small blocks, very latency sensitive. While OLTP databases tend to be normalized, data warehouses tend to be denormalized and therefore have lesser number of tables. For example, when querying the DB to find out who owns account 1234, it needs to join two tables, the Account-table with the Customer-table. In this example it is a two way join but it is possible for data warehousing systems to do many way joins (that is, joining multiple tables at once) and these are generally throughput bound.

###### Business Processes

An interesting way to look at the databases is its place in a business process. This provides you insight about the availability, concurrency and response requirements of the database. Typically OLTP databases are at the front of the process, customer-facing process, dramatically put they are in the line of fire. You want to have fast response, you want to read, insert and update data as fast as possible therefore the database are heavily normalized for reasons described above. When the OLTP database is performing slow or is unavailable it will typically impact revenue-generating processes. Data warehousing operations generally occur away from customer facing operations. Data is typically loaded into the data warehouse from multiple sources to provide the business insights into its day-to-day operations. For example, a business may want to understand from its data how it can drive quality and cost improvements. While we talk about a data warehouse as a single entity this is seldom the case. Many times you will find that a business has one large data warehouse and many so called ‘data marts’ that hang from it. Database proliferation is a real problem in the enterprise and managing all these databases and providing them the storage performance they need can be challenging. Let’s dive into the four database types to understand their requirements and the impact on architecture design:

###### OLTP

OLTP workloads have a good mix of read and write operations. It is latency sensitive, and it requires the support for high levels of concurrency. When talking about concurrency a good example are ATM machines. Each customer at an ATM machine is generating a connection doing a few simple instructions, however a bank typically has a lot of ATM machines servicing its many customers concurrently. If a customer wants to withdraw money, the process needs to read the records of the customer in the database. It needs to confirm that he or she is allowed to withdraw the money, and then it needs to record (write) the transaction. In DBA jargon that is a SQL SELECT statement followed by an UPDATE statement. A proper OLTP database should be able to handle a lot of users at the same time preferably with a low latency. It’s interactive in nature, meaning that latency impacts user experience. You cannot keep the customer waiting for a long time at the ATM machine or a bank teller. From an availability perspective you cannot afford to have the database go down, the connections cannot be lost, it just needs to be up and running all the time (24x7).

|  | OLTP | Reporting | OLAP | Analytics |
| --- | --- | --- | --- | --- |
| Availability | +++ |  |  |  |
| Concurrency | +++ |  |  |  |
| Latency sensitivity | +++ |  |  |  |
| Throughput oriented | + |  |  |  |
| Ad hoc | + |  |  |  |
| I/O Operations | Mix R/W |  |  |  |

###### Reporting

Reporting databases experience predominately read intensive operations and requires more throughput than anything else. Concurrency and availability are not as important for reporting databases as they are for OLTP. Characteristically workload is repeated read of data. Reporting is usually done when the users want to understand the performance of the business, for example how many accounts were opened this week, how many accounts were closed, is the private banking account team hitting it’s quota of acquiring new customers? Think of reporting as predictable requests, the user knows what data he wants to see and has a specific report design that structures the data in order needs to understand these numbers. This means, this report is repetitive which allow the DBA to design and optimize database and schema so that this query gets executed predictable and efficiently. Database design can be optimized for this report. Typical database schema designs for reporting include the Star Schema and the Snow Flake Schema. As it serves the back office processes, availability and concurrency are not a strict requirement of this kind of database. As long as the database is available when the report is required. Enhanced throughput helps tremendously.

|  | OLTP | Reporting | OLAP | Analytics |
| --- | --- | --- | --- | --- |
| Availability | +++ | + |  |  |
| Concurrency | +++ | + |  |  |
| Latency sensitivity | +++ | + |  |  |
| Throughput oriented | + | +++ |  |  |
| Ad hoc | + | + |  |  |
| I/O Operations | Mix R/W | Read Intensive |  |  |

###### OLAP

OLAP can be seen as the analytical counterpart of OLTP. Where OLTP is the original source of data, OLAP is the consolidation of data, typically originating from various OLTP databases. A common remark made in database world is that OLAP provides a multi-dimension view, meaning that you drill down the data coming from various sources and then analyze the data amongst different attributes. This workload is more ad-hoc in nature then reporting as you slice and dice the data in different ways depending on the nature of the query. The workload is primarily read intensive and can run complex queries involving aggregations of multiple databases, therefore its throughput oriented. An example of an OLAP query would be the amount of additional insurance services gold credit card customers were signing up for during the summer months.

|  | OLTP | Reporting | OLAP | Analytics |
| --- | --- | --- | --- | --- |
| Availability | +++ | + | + |  |
| Concurrency | +++ | + | + |  |
| Latency sensitivity | +++ | + | ++ |  |
| Throughput oriented | + | +++ | +++ |  |
| Ad hoc | + | + | ++ |  |
| I/O Operations | Mix R/W | Read Intensive | Read Intensive |  |

###### Analytics

Analytical workload is truly ad-hoc in nature. Whereas reporting aims to provide perspective of the numbers that are being presented, analytics provide insights in why the numbers are what they are. Reporting provides the how many new accounts where acquired by the private banking account team, analytics aims to provide insights why the private banking account team did not hit their quota in the last quarter. Analytics can query multiple databases and can be multi-step processes. Typically analytic queries write out large temporary results. Potentially it generates large intermediate results before slicing and dicing the temp data again. This means this data needs to be stored as fast as possible, the data is read again for the next query therefor read performance is crucial as well. Output is the input of the next query and this can happen multiple times, requiring both fast read and write performance otherwise your query will slow down dramatically. Another problem is the sort process, for example you are retrieving data that needs to be sorted however the dataset is so large that you can't hold everything in memory during the sort process resulting in spilling data to disk. Because analytics queries can be truly ad-hoc in nature it is difficult to design an effecient schema for it upfront. This makes analytics an especially difficult use case from a performance perspective.

|  | OLTP | Reporting | OLAP | Analytics |
| --- | --- | --- | --- | --- |
| Availability | +++ | + | + | + |
| Concurrency | +++ | + | + | + |
| Latency sensitivity | +++ | + | ++ | +++ |
| Throughput oriented | + | +++ | +++ | +++ |
| Ad hoc | + | + | ++ | +++ |
| I/O Operations | Mix R/W | Read Intensive | Read Intensive | Mix R/W |

###### Designing and testing your storage architecture in line with DB-workload

By having a better grasp of the storage performance requirements of each specific database you can now design your environment to suits its need. Understanding these requirements helps you to test the infrastructure more focused on the expected workload. Instead of running “your average db workload" in Iometer this allows you to test more towards latency or throughput oriented workloads when understanding what type of database will be used. The next article of this series dives into understanding whether tuning databases or storage architectures can solve performance.

###### Other parts of this series

[Part 2 – Data pipelines](http://frankdenneman.nl/2014/09/24/database-workload-characteristics-impact-storage-architecture-design-part-2-data-pipelines/ "Database workload characteristics and their impact on storage architecture design – part 2 – Data pipelines") [Part 3 – Ancillary structures for tuning databases](http://frankdenneman.nl/2014/09/29/database-workload-characteristics-impact-storage-architecture-design-part-3-ancillary-structures-tuning-databases/ "Database workload characteristics and their impact on storage architecture design – part 3 – Ancillary structures for tuning databases")
