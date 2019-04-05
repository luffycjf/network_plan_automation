# network_plan_automation

写在前面的，硬件模型的实现并不复杂，早就想做一个demo，但是苦于工作过于繁忙，搁置太久了。。。。终于咬咬牙把这篇文章和系统做出来了。

## 系统背景

在规划idc网络架构、选择网络设备、生成对应网络设备清单的时候，规模不大的公司可能是由厂商根据其需求来给出对应的方案。随着交换芯片能力的不断提升（Trident -〉Trident2 -〉Trident2+ -〉Trident 3，Tomahawk -〉Tomahawk+ -〉Tomahawk 2 -〉Tomahawk 3），idc网络从stp二层网络架构转换成三层ospf网络架构，再到现在主流的ebgp网络架构,网络协议层面定义基本趋于稳定了（因为目前并没有比ebgp更适合的大型网络路由协议,除非再开创一套新的协议）。而我们再看看idc网络硬件拓扑，可以发现随着二层网络的淘汰，核心交换机不再使用堆叠（或者思科vpc）这种架构设计，取而代之是收敛更快的ecmp架构。所以idc内部网络基本稳定在接入和核心交换机之间起三层协议，ecmp向上选择合适路径，而随着交换能力的提升，也只是下联带宽（1G,10G,25G,40G）和上下联收敛比的变化。所以我们（大一点的公司，可能是云厂商有多样业务）希望可以通过设备带宽，端口能力等条件来自动的算出网络架构和物料方案，大大减少人为因素对采购不准确的影响。这里介绍一下这套系统的实现算法。


## 硬件模型简述

我之前的文章也有介绍网络[硬件模型](https://jeffrycheng.com/2018/06/23/%E7%BD%91%E7%BB%9C%E5%BB%BA%E6%A8%A1%E9%9A%8F%E7%AC%94/)，这里基于我们这套系统所需要的数据介绍一下。<br/>

由于我们系统要能计算所有硬件物料方案，所以我们要把所有网络设备、配件、线缆都通过系统表示出来，我们把这些数据称之为设备硬件信息。<br/>
下面是数据库device_information的字段<br/>

* device_type: 设备类型（module,linecard,chassis,fabriccard,power,fan）<br/>
* model_name: 设备型号，唯一标识设备信息
* device_vendor: 设备厂商（HW\H3C\CISCO\JUNIPER\RUIJIE）<br/>
* device_description: 设备描述<br/>
* part_number: 设备物件编码<br/>
* module_bandwidth: 模块的带宽<br/>
* module_connectortype: 模块的接口类型(FC,LC,MPO,RJ45,SC,AOC)<br/>
* module_cabledistance: 模块的传输距离，单位m<br/>
注意到最后三个是模块（接口）特定的属性，正如门前面所说，除了设备之间的连接，决定一个架构的主要是其接口的带宽和能力（传输距离），所以这里三个参数至关重要。<br/>

除了设备信息数据库，我们还需要表示出设备之间的能力信息，比如究竟什么板卡、机框能插什么模块。<br/>
以下是设备间关系的信息数据库device_ability的字段<br/>

* model_name: 设备型号，唯一标识设备信息
* device_slot: 设备槽位号，比如机框的第几个板卡，板卡的第几个端口
* slot_model: 该槽位可以支持的硬件
* slot_bandwidth: 该槽位可插模块类物料的最大带宽
* slot_type: 该槽位可插物料的类型

通过这两个数据库，当我们知道某个设备他需要N个传输距离是10m带宽是10G，M个传输距离是100m带宽是40G的连接的时候，我们可以先根据模块信息找到合适的模块，遍历所有支持的模块组合找到合适的机框和板卡，这也是我们这套系统计算的核心。<br/>

## 互联关系
当我们已经有了能表述一台物理设备的硬件信息的能力后，我们要怎么知道这台设备究竟用什么硬件设备最合适，这就需要我们通过这台设备的互联关系算出来，我们用一个具体列子来看。<br/>
![](http://119.28.225.12:81/hm1.jpg)<br/>
如上图，假如我们希望最终构建的网络结构如图中所示。首先我们需要两种设备角色(role_name)，一种role_name是为ASW，一种role_name为PSW，我们先以ASW为列。<br/>
![](http://119.28.225.12:81/hm2.jpg)<br/>
如图所示，从ASW角度，他的数量(role_num)是4.每个ASW在这个需求中只需要并且必须和4台PSW都各有一个连接。因此我们需要有其互联角色名称（peer_role_name）、互联角色的数量（peer_role_num）以及互联单个角色的连接数量（peer_role_portnum）。这样我们就知道了角色ASW的全部连接数量，再结合在硬件模型中说的，定义这些连接接口的能力，带宽多大（peer_role_portbandwidth），传输距离多少（peer_role_portdistance）。根据这些信息我们就能去硬件模型数据库中搜寻符合条件的物理设备供架构设计者选择<br/>
这里ASW的定义已经完成了，有些人会问是不是PSW不需要定义了，当然不是。因为在定义ASW的时候我们并不知道在这个架构里面一共有多少个PSW,只是定义了一台ASW会和四台PSW互联，而且有可能PSW还和其他角色互联，比如如下所示。<br/>
![](http://119.28.225.12:81/hm3.jpg)<br/>
这个图中ASW依然满足我们上面的定义。但PSW一共有8台，在表述的PSW的时候，我们用role_name=PSW，role_num=8因为一共有8台，peer_role_name=ASW，peer_role_num=2这里需要注意因为一台PSW与两台ASW互联，peer_role_portnum、peer_role_portbandwidth、peer_role_portdistance和之前保持一致。这里你会发现ASW1、ASW3和PSW1-4互联，ASW2、ASW4和PSW5-8互联，其实这是和我们算法有关。<br/>
系统先根据其中一个架构角色，比如ASW,因为ASW的role_num是4，得知一共有ASW1、ASW2、ASW3、ASW4。再根据ASW的peer_role_portnum=1、peer_role_num=4，得知ASW上需要四个口，这样就将连接的半边算出来了，分别是ASW1四个口、ASW2四个口、ASW3四个口、ASW4四个口。再看对端PSW，因为role_num=8，所以有PSW1、PSW2、PSW3、PSW4、PSW5、PSW6、PSW7、PSW8八台。PSW连每个ASW有1个口，所以另外半边的连接则是（PSW1一个口、PSW2一个口、PSW3一个口、PSW4一个口、PSW5一个口、PSW6一个口、PSW7一个口、PSW8一个口）*2。<br/>
我们系统读取互联规则时，如果我们先读取到的role_name是ASW就会这样，如果先读取到role_name是PSW则是ASW1、ASW2和PSW1、3、5、7互联，ASW3、ASW4和PSW2、4、6、8互联。<br/>
那么有些人会问，如果我就想实现ASW1、ASW2和PSW1-4互联，ASW3、ASW4和PSW5-8互联怎么办呢，这种情况下可以当成两组互联关系来实现，因为在这种情况下，你在购买ASW1-2（连续的多台设备）完全没有对端PSW5-8的事情，所以完全可以分开两个计算单元，从架构角度也应该单独规划<br/>
完整的实现的过程还会考虑端口数量是否一致等情况，所以接下来我们来看一个完整的计算过程。<br/>

## 完整过程

1. 网络架构规划：这一步是构建一个通用基本的网络架构方案，需要什么样的设备，这些设备之间怎么互联。<br/>
比如我们规划一个IDC架构，需要48台接入交换机（ASW），8个100G传输距离是100M的上联，40个25G传输距离是10M的下联。
在设计系统的时候我认为模块的能力是通用的，不应该区分厂商具体能力，所以在设计模型的时候参照华为的模块名称，根据传输距离以及带宽、接口类型设计了统一的模块型号,以100G模块为例，如下表所示。<br/>

<table>
<tr><td>device_type</td><td>model_name</td><td>device_vendor</td><td>device_description</td><td>part_number</td><td>module_bandwidth</td><td>module_connectortype</td><td>module_cabledistance</td><td>module_wavelength</td></tr>
<tr><td>module</td><td>QSFP28-100G-SR4</td><td>UNIVERSAL</td><td>100GBase-SR4光模块-QSFP28-100G- 多模模块(850nm,0.1km,MPO)</td><td></td><td>100</td><td>MPO</td><td>100</td><td>850</td></tr>
<tr><td>module</td><td>QSFP28-100G-PSM4</td><td>UNIVERSAL</td><td>100GBase-PSM4 光模块-QSFP28-100G-单模模块(1310nm,0.5km,MPO)</td><td></td><td>100</td><td>MPO</td><td>300</td><td>1310</td></tr>
<tr><td>module</td><td>QSFP-100G-CWDM4</td><td>UNIVERSAL</td><td>100GBase-CWDM4 光模块-QSFP28-100G- 单模模块(1310nm,2km,LC)</td><td></td><td>100</td><td>MPO</td><td>2000</td><td>1310</td></tr>
<tr><td>module</td><td>QSFP28-100G-LR4</td><td>UNIVERSAL</td><td>100GBase-LR4 光模块-QSFP28-100G- 单模模块(1310nm,10km,LC)</td><td></td><td>100</td><td>MPO</td><td>10000</td><td>1310</td></tr>
<tr><td>module</td><td>QSFP-100G-ER4-Lite</td><td>UNIVERSAL</td><td>100GBase-ER4-Lite 光模块-QSFP28-100G- 单模模块(1310nm,30km(FECOFF),40km(FEC ON),LC)</td><td></td><td>100</td><td>MPO</td><td>40000</td><td>1310</td></tr>
<tr><td>module</td><td>QSFP-100GAOC</td><td>UNIVERSAL</td><td>有源光缆-QSFP28-100G-(850nm,10m,AOC)</td><td></td><td>100</td><td>AOC</td><td>10</td><td>850</td></tr>
</table>

<br/>
ASW的具体定义如下，运行network_plan.py -c。<br/>
![](http://119.28.225.12:81/hm4.png)<br/>
同样我们需要定义PSW，一共四台，下联100G需要和48台ASW，上联100G需要和4台DSW互联。<br/>
![](http://119.28.225.12:81/hm5.png)<br/>
最后得到生成规划文件如下：<br/>

```javascript
[{
	'role_num': '48',
	'role_name': 'ASW',
	'peer_role': [{
		'peer_role_name': 'PSW',
		'peer_role_portnum': '1',
		'peer_role_portbandwidth': '100',
		'peer_role_portdistance': ['100'],
		'peer_role_num': '8'
	}, {
		'peer_role_name': 'SE',
		'peer_role_portnum': '1',
		'peer_role_portbandwidth': '25',
		'peer_role_portdistance': ['10'],
		'peer_role_num': '40'
	}]
}, {
	'role_num': '8',
	'role_name': 'PSW',
	'peer_role': [{
		'peer_role_name': 'ASW',
		'peer_role_portnum': '1',
		'peer_role_portbandwidth': '100',
		'peer_role_portdistance': ['100'],
		'peer_role_num': '48'
	}, {
		'peer_role_name': 'DSW',
		'peer_role_portnum': '6',
		'peer_role_portbandwidth': '100',
		'peer_role_portdistance': ['2000'],
		'peer_role_num': '4'
	}]
}]
```

2. 根据规划文件，选取合适的硬件并规划端口使用规则。<br/>
![](http://119.28.225.12:81/hm6.png)<br/>
如图所示，系统会根据连接需求去硬件模型数据库中找出满足符合要求的硬件方案，具体过程可以查看前面硬件模型介绍，选择对应的硬件物料方案即可。接下来会根据所选的硬件选取对应的板卡和端口等硬件规划。<br/>
![](http://119.28.225.12:81/hm7.png)<br/>
![](http://119.28.225.12:81/hm8.png)<br/>
选择完成后会生成一个关于该硬件方案的文件夹，并包含每个架构角色的硬件配套方案和互联关系arch_conn。<br/>

```javascript
[root@VM_centos H1]# ll
total 16
-rw-r--r-- 1 root root  308 Apr  5 18:05 arch_conn
-rw-r--r-- 1 root root 2805 Apr  5 18:04 ASW
-rw-r--r-- 1 root root 6422 Apr  5 18:05 PSW
```

3. 最后选取本次需要建设的设备数量，生成对应的连接关系和采购物料表。<br/>
![](http://119.28.225.12:81/hm9.png)<br/>
这一步就是根据前面的arch_conn生成全量的连接关系。arch_conn内容如下：<br/>

```javascript
[{
	'role_num': '48',
	'role_name': 'ASW',
	'peer_roles': [{
		'peer_role_name': 'PSW',
		'peer_role_num': '8'
	}, {
		'peer_role_name': 'SE',
		'peer_role_num': '40'
	}]
}, {
	'role_num': '8',
	'role_name': 'PSW',
	'peer_roles': [{
		'peer_role_name': 'ASW',
		'peer_role_num': '48'
	}, {
		'peer_role_name': 'DSW',
		'peer_role_num': '4'
	}]
}]
```
如上所示，先读取role_name为ASW，根据peer_role_name进行分类，如果peer_role_name也在role_name中，那么就会根据role_name为peer_role_name的role_num计算对端设备名称和端口，否则直接根据peer_roles中peer_role_num生成对端名称和空端口。<br/>
生成完全量连接后，再根据本次需要建设的序号，生成本次建设设备名称去全量的表中进行筛选，得到本次建设的连接关系。<br/>
![](http://119.28.225.12:81/hm10.png)<br/>
最后根据本次连接，去查找每个设备的硬件配套信息，因为硬件配套中非常详细的记录了一个设备每个槽位对应的物料，以及每个端口对应的角色、模块型号、所属板卡号，根据这些信息就能算出本次需要使用的硬件物料信息，最后在硬件版本目录下生成完整的方案表order_scheme_xx.xls。
![](http://119.28.225.12:81/hm11.png)<br/>
![](http://119.28.225.12:81/hm12.png)<br/>
![](http://119.28.225.12:81/hm13.png)<br/>

最后附上[github下载地址](https://github.com/luffycjf/network_plan_automation)，目前还有很多功能待完善，硬件信息可以通过
./network_plan.py -if xx.xlsx和./network_plan.py -ia xx.xlsx分别倒入物料和能力信息，当前hardware_model.sql数据库包含了h3c\hw\cisco\ruijie最新主流idc交换机及其物料信息。<br/>
新建数据库
mysql -u root -p
create database hardware_model;
数据库导入方式
mysql -u root -p hardware_model < hardware_model.sql
配置数据库的密码在config.py中：<br/>

```javascript
database = 'hardware_model'
databaseuser = 'hardwareuser'
databasepassword = 'hardwarepass'
databasehost = 'localhost'
```
<br/>
如果有堆叠需求，可以参照如下定义：

![](http://119.28.225.12:81/hm14.png)<br/>
从头规划可以./network_plan.py -c或者./network_plan.py -c 指定之前规划好的架构文件。<br/>
./network_plan.py -ca 指定特定的硬件版本文件<br/>


今天就写这么多，假期又这么过了一天。。。。。








