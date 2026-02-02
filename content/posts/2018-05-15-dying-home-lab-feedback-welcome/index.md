---
title: "Dying Home Lab - Feedback Welcome"
date: 2018-05-15
categories: 
  - "home-lab"
  - "vmware"
---

The servers in my home lab are dying on a daily basis. After [four years](http://frankdenneman.nl/2014/03/27/vsphere-5-5-home-lab/) of active duty, I think they have the right to retire. So I need something else. But what? I can't rent lab space as I work with unreleased ESXi code. I've been waiting for the Intel Xeon D 21xx Supermicro systems, but I have the feeling that Elon will reach Mars before we see these systems widely available. The system that I have in mind is the following:

- Intel Xeon Silver 4108 - 8 Core at 1.8 GHz (85TDP)
- Supermicro X11SPM-TF (6 DIMMs, 2 x 10 GbE)
- 4 x Kingston Premier 16GB 2133
- Intel Optane M.2 2280 32 GB

**CPU** [Intel Xeon Silver 4108 8 Core](https://ark.intel.com/products/123544/Intel-Xeon-Silver-4108-Processor-11M-Cache-1_80-GHz?q=silver%204108). I need to have a healthy number of cores in my system to run some test workload. Primarily to understand host and cluster scheduling. I do not need to run performance tests, thus no need for screaming fast CPU cores. TDP value of 85W. I know there is a 4109T with a TDP value of 70W, but they are very hard to get in the Netherlands. **Motherboard** [Supermicro X11SPM-TF](https://www.supermicro.com/products/motherboard/Xeon/C620/X11SPM-TF.cfm).Rocksolid Supermicro, 2 x Intel X722 10GbE NICs onboard and IPMI. **Memory** Kingston Premier 4 x 16 GB 2133 MHz. DDR4 money is nearing HP Printer Ink prices, 2133 MHz is fast enough for my testing, and I don't need to test 6 channels of RAM at the moment. The motherboard is equipped with 6 DIMM slots, so if memory prices are reducing, I can expand my system. **Boot Device** Intel Optane M.2 32 GB. ESXi still needs to have a boot device, no need to put in 256 GB SSD. This is the config I'm considering. What do you think? Any recommendations or alternate views?
