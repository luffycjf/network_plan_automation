#!/usr/bin/python
#-*- coding:utf-8 -*-
import datetime,xlrd,xlwt,sys,copy,time
import MySQLdb
import re,os
from prettytable import PrettyTable

try:
    import config.py
except:
    database = 'hardware_model'
    databaseuser = 'hardwareuser'
    databasepassword = 'hardwarepass'
    databasehost = 'localhost'


class mysqlopt:
    def __init__(self, dbhost, dbuser ,dbpass, dbname):
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
    def opendb(self):
        self.db = MySQLdb.connect(self.dbhost,self.dbuser,self.dbpass,self.dbname,charset='utf8' )
        self.curs = self.db.cursor()
    def optdata(self,sql):
        try:
            self.curs.execute(sql)
            self.db.commit()
            return 'success'
        except:
            self.db.rollback()
            return 'fail'
    def getdata(self,sql):
        try:
            self.curs.execute(sql)
            result = self.curs.fetchall()
            return result
        except:
            return ''
    def closedb(self):
        self.db.close()

def newdb(dbuser,dbpass,dbname,dbhost):
    db = mysqlopt(dbhost=dbhost,dbuser=dbuser,dbpass=dbpass,dbname=dbname)
    db.opendb()
    return db
    
def change_float_str(a_str):
    a_str = str(a_str).rstrip('0').rstrip('.') if str(a_str)[-2:] == '.0' else str(a_str)
    return a_str.strip()

def newability(db,model_names,device_slots,slot_models,slot_bandwidths,submission_date,slot_types):
    for model_name,device_slot,slot_model,slot_bandwidth,slot_type in zip(model_names,device_slots,slot_models,slot_bandwidths,slot_types):
        model_name = change_float_str(model_name)
        device_slot = change_float_str(device_slot)
        slot_model = change_float_str(slot_model)
        slot_bandwidth = change_float_str(slot_bandwidth)
        slot_type = change_float_str(slot_type)
        sql = "DELETE FROM device_ability WHERE device_slot = '%s' and model_name = '%s' and slot_bandwidth = '%s' and slot_type = '%s'"
        params = (device_slot.strip(),model_name.strip(),slot_bandwidth.strip(),slot_type.strip())
        db.optdata(sql%params)
        sql = "INSERT INTO device_ability(model_name,device_slot,slot_model,slot_bandwidth,submission_date,slot_type)VALUES ('%s','%s','%s','%s','%s','%s')"
        params = (model_name,device_slot,slot_model,slot_bandwidth,submission_date,slot_type)
        db.optdata(sql%params)
    
def newdevice(db,device_types,model_names, device_vendors, device_descriptions, part_numbers, submission_date, module_bandwidths, module_connectortypes, module_cabledistances, module_wavelengths):
    for device_type, model_name, device_vendor, device_description, part_number, module_bandwidth, module_connectortype, module_cabledistance, module_wavelength in zip(device_types, model_names, device_vendors, device_descriptions, part_numbers, module_bandwidths, module_connectortypes, module_cabledistances, module_wavelengths): 
        device_type = change_float_str(device_type)
        model_name = change_float_str(model_name)
        device_vendor = change_float_str(device_vendor)
        part_number = change_float_str(part_number)
        module_bandwidth = change_float_str(module_bandwidth)
        module_connectortype = change_float_str(module_connectortype)
        module_cabledistance = change_float_str(module_cabledistance)
        module_wavelength = change_float_str(module_wavelength)
        sql = "DELETE FROM device_information WHERE model_name = '%s'"
        params = model_name
        db.optdata(sql%params)
        sql = "INSERT INTO device_information(device_type,model_name,device_vendor,device_description,part_number,submission_date,module_bandwidth,module_connectortype,module_cabledistance,module_wavelength)VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
        params = (device_type,model_name,device_vendor,device_description,part_number,submission_date,module_bandwidth,module_connectortype,module_cabledistance,module_wavelength) 
        db.optdata(sql%params)

def insertdeviceinfo(filename):
    dbuser = databaseuser
    dbpass = databasepassword
    dbname = database
    dbhost = databasehost
    ndb = newdb(dbuser,dbpass,dbname,dbhost)
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0) 
    device_types = sheet.col_values(0)[1:]
    model_names = sheet.col_values(1)[1:]
    device_vendors = sheet.col_values(2)[1:]
    device_descriptions = sheet.col_values(3)[1:]
    part_numbers = sheet.col_values(4)[1:]
    submission_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    module_bandwidths = sheet.col_values(5)[1:]
    module_connectortypes = sheet.col_values(6)[1:]
    module_cabledistances = sheet.col_values(7)[1:]
    module_wavelengths = sheet.col_values(8)[1:]
    newdevice(ndb,device_types=device_types,model_names=model_names, device_vendors=device_vendors,device_descriptions=device_descriptions,part_numbers=part_numbers,submission_date=submission_date,module_bandwidths=module_bandwidths,module_connectortypes=module_connectortypes,module_cabledistances=module_cabledistances,module_wavelengths= module_wavelengths)
    ndb.closedb()

def insertdeviceability(filename):
    dbuser = databaseuser
    dbpass = databasepassword
    dbname = database
    dbhost = databasehost
    ndb = newdb(dbuser,dbpass,dbname,dbhost)
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)
    model_names = sheet.col_values(0)[1:]
    device_slots = sheet.col_values(1)[1:]
    slot_types = sheet.col_values(2)[1:]
    slot_models = sheet.col_values(3)[1:]
    slot_bandwidths = sheet.col_values(4)[1:]
    submission_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    newability(db=ndb,model_names=model_names,device_slots=device_slots,slot_models=slot_models,slot_bandwidths=slot_bandwidths,submission_date=submission_date,slot_types=slot_types)
    ndb.closedb()

def help():
    helpstr = '''
    -if import hardware device information 
    -ia import hardware device abitlity
    -c Calculate scheme
    -h help
            
    '''
    print (helpstr)
    

# 合并列表，递归遍历所有可能的子函数
def mergelist(alist,blist):
    clist = []
    for i in alist:
        for j in blist:
            if str(type(i)) == "<type 'list'>":
                x= []
                x = copy.deepcopy(i)
                x.append(j)
                clist.append(x)
            else:
                x = [i,j]
                clist.append(x)
    return clist        
                                

# 递归生成所有模块的组合方案
def iterateover(alist):
    if len(alist) == 1:
        return alist[0]
    return mergelist(iterateover(alist[1:]),alist[0])

def iterateover_plus(alist):
    nlist = []
    if len(alist) == 1:
        for x in alist :
            for y in x:
                nlist.append([y])
    elif len(alist) == 0:
        nlist = []
    else:
        nlist = iterateover(alist)   
    return nlist


#端口比较
def compareinterface(a_interface,b_interface):
    for i in range(len(a_interface.split('/'))):
        try:
            if int(re.sub('[a-zA-Z]','',a_interface.split('/')[i])) > int(re.sub('[a-zA-Z]','',b_interface.split('/')[i])):
                return True
            elif int(re.sub('[a-zA-Z]','',a_interface.split('/')[i])) < int(re.sub('[a-zA-Z]','',b_interface.split('/')[i])):
                return False
        except:
            return False
    return False

# 排序端口    
def interfacesort(interface_list):
    for i in range(len(interface_list)):
        for j in range(i+1,len(interface_list)):
            if compareinterface(interface_list[i],interface_list[j]):
                interface_list[i],interface_list[j] = interface_list[j],interface_list[i]
    return interface_list

# 混合接口前缀排序
def deviceintsort(interface_list):
    n_interface_list = []
    for intprefix in set([re.sub('\d','',il.split('/')[0]) for il in interface_list]):
        m_interface_list = []
        for inl in interface_list:
            if re.sub('\d','',inl.split('/')[0]) == intprefix:
                m_interface_list.append(inl)
        n_interface_list += interfacesort(m_interface_list)
    return n_interface_list


# 获取所选编号
def getnum(num_str):
    num_list = []
    try:
        for ns in num_str.split(','):
            if len(ns.split('-')) == 2:
                num_list += range(int(ns.split('-')[0]),int(ns.split('-')[1])+1)
            else:
                num_list.append(ns.split('-')[0])
        num_list = [ str(i) for i in sorted(list(set([ int(nl) for nl in num_list ])))]
    except:
        num_list = []
    return num_list

# 去重结果
def deldouble(a_list):
    b_list = []
    for a in a_list:
        a_result = 0
        for b in b_list:
            if a == b:
                a_result = 1
                break
        if a_result == 0:
            b_list.append(a)
    return b_list    

'''
# 分隔列表
def splitlist(a_list,num):
    if len(a_list)%num != 0:
        a_list = a_list + a_list[:num - len(a_list)%num]   
    b_list = []
    n = 0
    a_num = num
    while a_num <= len(a_list):
        b_list.append(a_list[n:a_num])
        n = a_num
        a_num = n+num
    return b_list
'''            

# 根据模块需求找到符合要求的盒式设备方案
def get_avail_device_nochassis (ndb,avail_modules_list):
    interface_prefix = {'100':'H','25':'TF','40':'FG','10':'T','400':'FH','1':'G'}
    avail_solution = []
    for avail_modules in avail_modules_list:
        sql = "select model_name,device_slot,slot_model from device_ability where slot_model like '%%%s%%' and slot_type = 'module'"%avail_modules[0]['module']
        result_ability = ndb.getdata(sql)
        if result_ability == ():
            continue
        for ra in set([i[0] for i in result_ability]):
            sql = "select device_type from device_information where model_name = '%s'"%ra
            result_type = ndb.getdata(sql)
            if result_type == ():
                continue
            if result_type[0][0] != 'chassis':
                continue
            sql = "select device_slot,slot_bandwidth,slot_model from device_ability where model_name = '%s' and slot_type = 'module'"%ra
            results_ability = ndb.getdata(sql)
            device_ability= { interface_prefix[da[1]]+da[0]:da[2] for da in results_ability}
            a_result = 0
            for am in avail_modules:
                result = 1
                num = 0
                for device_ability_m in interfacesort([i for i in device_ability]):
                    if am['module'] in device_ability[device_ability_m]:
                        num += 1
                        device_ability.pop(device_ability_m)
                    if num >= int(am['num']):
                        result = 0
                        break
                if result == 1:
                    a_result = 1
                    break

            if a_result == 0:
                solution = {}
                solution['chassis'] = ra
                solution['module'] = avail_modules
                avail_solution.append(solution)
    return avail_solution


# 根据模块需求找到符合要求的框式设备方案    
def get_avail_device_chassis (ndb,avail_modules_list):
    interface_prefix = {'100':'H','25':'TF','40':'FG','10':'T','400':'FH','1':'G'}
    avail_solutions = []
    avail_solution = []
    for avail_modules in avail_modules_list:
        avail_linecard_solution = []
        for avail_module in avail_modules:
            sql = "select model_name  from device_ability where slot_model like '%%%s%%'"%avail_module['module']
            result_model = ndb.getdata(sql)
            avail_ability_model = [ i[0] for i in result_model ]
            avail_linecard_ability = []
            for a in set(avail_ability_model):
                sql = "select device_type from device_information where model_name = '%s'"%a
                result_type = ndb.getdata(sql)    
                if result_type == ():
                    continue
                model_type = result_type[0][0]
                if model_type == 'linecard':
                    num = avail_ability_model.count(a)
                    module_num = int(avail_module['num'])
                    linecard_num = int(module_num/num)+1
                    linecard_reserve_port_num = num - int(module_num%num)
                    avail_linecard_ability.append({'linecard':a,'linecard_num':linecard_num,'linecard_reserve_port_num':linecard_reserve_port_num,'all_num':num})
            avail_linecard_solution.append(avail_linecard_ability)
        avail_linecard_solutions = iterateover_plus(avail_linecard_solution)
        avail_linecard_solutions = deldouble(avail_linecard_solutions)
        avail_linecard_solutions_list = []
        for als in avail_linecard_solutions:
            a = {}
            for m,n in set([(i['linecard'],i['all_num']) for i in als]):    
                linecard_num = 0
                linecard_reserve_port_num = 0
                for m1 in als:
                    if m1['linecard'] == m:
                        linecard_num += m1['linecard_num']
                        linecard_reserve_port_num += m1['linecard_reserve_port_num']
                if linecard_reserve_port_num >= n:
                    linecard_num = linecard_num - int(linecard_reserve_port_num/n)
                    linecard_reserve_port_num = int(linecard_reserve_port_num%n)
                a[m] = linecard_num
            avail_linecard_solutions_list.append(a)
        avail_linecard_solutions_list = deldouble(avail_linecard_solutions_list)
        for alsl in avail_linecard_solutions_list:
            sql = "select model_name,device_slot,slot_model from device_ability where slot_model like '%%%s%%'"%alsl.keys()[0]
            result_ability = ndb.getdata(sql)
            for dm in set([rb[0] for rb in result_ability]):
                device_ability = { da[1]:da[2] for da in result_ability if da[0] == dm }
                a_result = 0
                for alslm in alsl:
                    result = 1
                    num = 0
                    for device_ability_m in interfacesort([i for i in device_ability]):
                        if alslm in device_ability[device_ability_m]:
                            num += 1
                            device_ability.pop(device_ability_m)
                        if num >= alsl[alslm]:
                            result = 0
                            break
                    if result == 1:
                        a_result = 1
                        break
                if a_result == 0:
                    solution = {}
                    solution['chassis'] = dm
                    solution['linecard'] = alsl
                    solution['module'] = avail_modules
                    avail_solutions.append(solution)
        avail_solutions = deldouble(avail_solutions)
        if avail_solutions != []:
            avail_vendor_device = []
            for ass in avail_solutions:
                sql = "select device_vendor from device_information where model_name = '%s'"%ass['chassis']
                result_vendor = ndb.getdata(sql)
                if result_vendor == ():    
                    continue
                device_vendor = result_vendor[0][0]
                sql = "select * from device_ability where model_name = '%s' and slot_type = 'linecard'"%ass['chassis']
                result_ability = ndb.getdata(sql)
                device_linecard_num = len(result_ability)
                avail_vendor_device.append({'vendor':device_vendor,'model':ass['chassis'],'num':device_linecard_num})
            avail_model = []
            for vendor in set([i['vendor'] for i in avail_vendor_device]):
                n = 100
                m = ''
                for avd in avail_vendor_device:
                    if avd['vendor'] == vendor:
                        if avd['num'] < n:
                            m = avd['model']
                            n = avd['num']
                avail_model.append(m)
            for ass in avail_solutions:
                if ass['chassis'] in avail_model:
                    avail_solution.append(ass) 
    avail_solution = deldouble(avail_solution)
    return avail_solution





# 生成需求单
def buildplanfile():
    device_role = []
    print (u'********************开始规划架构*********************** ')
    print ('\n')
    while True:
        print '\n'
        device_role_dict = {}
        print (u'请输入一个新的架构角色名称，按q退出 :')
        role_name = raw_input('please input an new role name,input q to quit: ')
        if role_name == 'q' or role_name == '':
            break
        while True:
            print (u'请输入%s的最大数量 :'%role_name)
            role_num = raw_input('please input the number of the %s: '%role_name)
            if role_num.isdigit():
                break
        device_role_dict['role_name'] = role_name
        device_role_dict['role_num'] = role_num
        device_role_dict['peer_role'] = []
        print (u'\n开始定义该架构角色的互联关系\n')        
        while True:
            peer_device_role_dict = {}
            print (u'请输入一个互联架构角色名称,按q退出: ')
            peer_role_name = raw_input('please input an peer role name for %s,input q to quit:'%role_name)
            if peer_role_name == 'q' or peer_role_name == '':
                break
            while True:
                print (u'请输入单个%s设备与多少个%s互联: '%(role_name,peer_role_name))
                peer_role_num = raw_input('please input the device number of %s connect to one %s: '%(peer_role_name,role_name))
                if peer_role_num.isdigit():
                    break
            while True:
                print (u'请输入单个%s与单个%s间的端口数量: '%(role_name,peer_role_name))
                peer_role_portnum = raw_input('please input the number of the ports between one %s and one %s: '%(role_name,peer_role_name))
                if peer_role_portnum.isdigit():
                    break
            while True:
                print (u'请输入这些互联端口的带宽(G): ')        
                peer_role_portbandwidth = raw_input('please input the bandwidth(G) for these ports: ')
                if peer_role_portbandwidth.isdigit():
                    break
            while True:
                print (u'请输入这些端口所需传输距离(M)，可以输入多个值如5,10,100,300,2000: ')
                peer_role_portdistance = raw_input('please input the max distance for transmission distance(M),you can input a list like 5,10,100,300,2000: ')
                peer_role_portdistance = getnum(peer_role_portdistance)
                for prp in peer_role_portdistance:
                   if not  prp.isdigit():
                      peer_role_portdistance.remove(prp)
                if peer_role_portdistance != []: 
                    break
            peer_device_role_dict['peer_role_name'] = peer_role_name
            peer_device_role_dict['peer_role_num'] = peer_role_num
            peer_device_role_dict['peer_role_portnum'] = peer_role_portnum
            peer_device_role_dict['peer_role_portbandwidth'] = peer_role_portbandwidth
            peer_device_role_dict['peer_role_portdistance'] = peer_role_portdistance
            device_role_dict['peer_role'].append(peer_device_role_dict)
        device_role.append(device_role_dict)
    while True:
        print u'请输入该架构名称'
        arch_version = raw_input('please input arch version:\n')
        if arch_version != '':
            break
    filename = arch_version.strip()
    with open(filename,'w') as f:
        f.write(str(device_role))
    return filename


#根据需求单计算满足需求的硬件方案
def calculatescheme(demand_file):
    with open(demand_file,'r') as f:
        device_command = f.read()
    device_role_command = 'device_role='+device_command
    exec(device_role_command) in locals()
    dbuser = databaseuser
    dbpass = databasepassword
    dbname = database
    dbhost = databasehost
    ndb = newdb(dbuser,dbpass,dbname,dbhost)
    print '\n'
    print u'********************开始定硬件规划*********************** '
    print '\n'
    while True:
        print u'请输入这个硬件方案的名称:'
        hardware_version = raw_input('please input this hardware plan version:\n')
        if hardware_version != '':
            break
    if not os.path.exists(hardware_version):
        os.makedirs(hardware_version)
    arch_conn = []
    for role in device_role:
        avail_modules = []
        for peer_role in role['peer_role']:
            if len(peer_role['peer_role_portdistance']) == 1:
                sql = "SELECT model_name FROM device_information WHERE module_bandwidth = '%s' and module_cabledistance = '%s'"%(peer_role['peer_role_portbandwidth'],peer_role['peer_role_portdistance'][0])
            else:
                sql_list = []
                for pp in peer_role['peer_role_portdistance']:
                    sql_list.append("module_cabledistance = '%s'"%pp)
                sql = "SELECT model_name FROM device_information WHERE module_bandwidth = '%s' and (%s)"%(peer_role['peer_role_portbandwidth'],(' or ').join(sql_list))
            result_module = ndb.getdata(sql)
            portnum = int(peer_role['peer_role_portnum'])*int(peer_role['peer_role_num'])
            avail_modules.append([ {'module':i[0],'num':portnum,'role':peer_role['peer_role_name']} for i in result_module ])
        avail_modules_list = iterateover_plus(avail_modules)
        avail_solution = get_avail_device_nochassis (ndb,avail_modules_list)
        if avail_solution == []:
            avail_solution = get_avail_device_chassis (ndb,avail_modules_list)
        if  avail_solution == []:
            print u'没有找到符合要求的%s硬件设备！'%role['role_name']
            print 'do not have avail hardware device for %s'%role['role_name']
            continue
        n = 1
        print u'%s可选的硬件设备组合如下：'%role['role_name']
        print '%s avail device solution as follows :'%role['role_name']
        for a_s in avail_solution:
            a_s['num'] = str(n)
            if a_s.has_key('linecard'):
                print '%s .  device: %s  linecard: %s  module:%s '%(a_s['num'],str(a_s['chassis']),str(a_s['linecard']),str(a_s['module']))
            else:
                print '%s .  device: %s  module: %s '%(a_s['num'],str(a_s['chassis']),str(a_s['module']))
            n += 1
        while True:
            print u'请选择一个方案，输入对应序号：'
            solution_num = raw_input("please select one solution: ")
            if solution_num in [str(i) for i in range (1,n)]:
               break 
        solution = {}
        for a_s in avail_solution:
            if a_s['num'] == solution_num:
                solution = a_s
                break
        device_solution = {}
        interface_prefix = {'100':'H','25':'TF','40':'FG','10':'T','400':'FH','1':'G'}
        if solution.has_key('linecard'):
            linecard_ability = {}
            port_ability = {}
            for linecard,num in solution['linecard'].items():
                sql =  "select device_slot from device_ability where slot_model like '%%%s%%' and model_name = '%s'"%(linecard,solution['chassis'])
                result_slot = ndb.getdata(sql)
                avial_slot = [ j for j in  [ i[0] for i in result_slot ] if j not in linecard_ability.keys() ]
                linecard_list = [ 'slot:'+slot+'.'+linecard for slot in avial_slot]
                col = PrettyTable()
                col.add_column(solution['chassis'],linecard_list)                
                print col
                print u'请为%s选择%s个合适的槽位'%(linecard,num)
                print 'please select %s %s device slots for %s :%s'%(num,solution['chassis'],linecard,(',').join(avial_slot))
                slot_str = raw_input()
                slot = getnum(slot_str)
                slot = avial_slot[:num]
                while len(slot) < num or  [s for s in slot if s not in avial_slot]:
                    print ("slot num is not enough and must use ',' to split,please input again")
                    slot_str = raw_input()
                    slot = getnum(slot_str)
                sql = "select slot_model,device_slot,slot_bandwidth from device_ability where model_name = '%s'"%linecard
                result_port = ndb.getdata(sql)
                for i in slot:
                    linecard_ability[i] = linecard
                    port_ability.update({interface_prefix[j[2]]+i+'/'+j[1]:j[0] for j in result_port })
            device_ability_table = {}
            n = 1
            for i in set([ re.sub('[a-zA-Z]','',j.split('/')[0]) for j in port_ability]):
                device_ability_table[i] = []
            for pa in interfacesort([ i for i in port_ability]):
                chassis_num = re.sub('[a-zA-Z]','',pa.split('/')[0])
                device_ability_table[chassis_num].append('%s.%s idle'%(str(n),pa))
                n += 1
            table_len = max([len(device_ability_table[i]) for i in device_ability_table])
            for dat in device_ability_table:
                if len(device_ability_table[str(dat)]) < table_len:
                    device_ability_table[str(dat)] = device_ability_table[str(dat)]+idle_table
            for sm in solution['module']:
                for dat in device_ability_table:
                    for dati in  range(len(device_ability_table[dat])):
                        if sm['module'] in port_ability[device_ability_table[dat][dati].split()[0].split('.')[1]]:
                            device_ability_table[dat][dati] = device_ability_table[dat][dati].replace('idle','avail')
                        else:
                            device_ability_table[dat][dati] = device_ability_table[dat][dati].replace('avail','idle')
                col = PrettyTable()
                for dat in sorted([ int(j) for j in device_ability_table ]):
                    col.add_column(str(dat)+':'+linecard_ability[str(dat)],device_ability_table[str(dat)])
                print col
                print u'请为%s选%s个择状态为avail的可用端口序号，单个选择用,分隔，连续多个可用-'%(sm['role'],str(sm['num']))
                print 'please select %s avail ports num for %s :'%( str(sm['num']),sm['role'])
                input_port_list = []
                avail_port_list = []
                for dat in device_ability_table:
                    for dati in device_ability_table[dat]:
                        if 'avail' in dati:
                            avail_port_list.append(dati.split('.')[0])
                while True:
                    port_num = raw_input()
                    input_port_list = getnum(port_num)
                    input_port_list = [str(i) for i in input_port_list]
                    if [ ipl for ipl in input_port_list if ipl not in avail_port_list ]:
                        print 'please input avail ports , your input ports include unavail ports:'
                    elif len(input_port_list) != sm['num']:
                        print 'please input %s ports'%str(sm['num'])
                    else:
                         break
                for ipl in input_port_list:
                    for dat in device_ability_table:
                        for dati in range(len(device_ability_table[dat])):
                            if device_ability_table[dat][dati].split('.')[0] == ipl:
                                device_ability_table[dat][dati] = device_ability_table[dat][dati].replace('avail',sm['role'])
            for dat in device_ability_table:
                for dati in range(len(device_ability_table[dat])):
                    device_ability_table[dat][dati] = device_ability_table[dat][dati].replace('avail','idle')
            col = PrettyTable()
            for dat in sorted([ int(j) for j in device_ability_table ]):
                col.add_column(str(dat)+':'+linecard_ability[str(dat)],device_ability_table[str(dat)])
            print col
            device_port_ability = {}
            for pa in port_ability:
                for dat in device_ability_table:
                    for dati in device_ability_table[dat]:
                        if pa == dati.split('.')[1].split()[0]:
                            for sm in solution['module']:
                                if dati.split()[1] == sm['role']:
                                    device_port_ability[pa] = {}
                                    device_port_ability[pa]['module'] = sm['module']
                                    device_port_ability[pa]['role'] = sm['role']
                                    device_port_ability[pa]['linecard_num'] = dat
            device_solution['linecard'] = linecard_ability 
            device_solution['port'] = device_port_ability
            device_solution['chassis'] = solution['chassis']
        else:
            port_ability = {}
            sql = "select slot_model,device_slot,slot_bandwidth from device_ability where model_name = '%s' and slot_type = 'module'"%solution['chassis']
            result_port = ndb.getdata(sql)
            port_ability = {interface_prefix[j[2]]+j[1].strip():j[0].strip() for j in result_port }
            device_ability_table = []
            n = 1
            for ipa in  deviceintsort([ pa for pa in port_ability ]):
                device_ability_table.append('%s.%s idle'%(str(n),ipa))
                n += 1
            for sm in solution['module']:
                for dat in range(len(device_ability_table)):
                    if sm['module'] in port_ability[device_ability_table[dat].split('.')[1].split()[0]]:
                        device_ability_table[dat] = device_ability_table[dat].replace('idle','avail')
                    else:
                        device_ability_table[dat] = device_ability_table[dat].replace('avail','idle')
                col = PrettyTable()
                col.add_column(solution['chassis'],device_ability_table)
                print col
                print u'请为%s选择%s个状态为avail的可用端口序号，单个选择用,分隔，连续多个可用-'%(sm['role'],str(sm['num']))
                print 'please select %s avail ports num for %s :'%( str(sm['num']),sm['role'])
                input_port_list = []
                avail_port_list = [ dat.split('.')[0] for dat in device_ability_table if 'avail' in dat ]
                while True:
                    port_num = raw_input()
                    input_port_list = getnum(port_num)
                    if [ ipl for ipl in input_port_list if ipl not in avail_port_list ]:
                        print 'please input avail ports , your input ports include unavail ports:'
                    elif len(input_port_list) != sm['num']:
                        print 'please input %s ports'%str(sm['num'])
                    else:
                        break
                for ipl in input_port_list:
                    for dat in range(len(device_ability_table)):
                        if device_ability_table[dat].split('.')[0] == ipl:
                            device_ability_table[dat] = device_ability_table[dat].replace('avail',sm['role'])
            for dat in range(len(device_ability_table)):
                device_ability_table[dat] = device_ability_table[dat].replace('avail','idle')
            col = PrettyTable()
            col.add_column(solution['chassis'],device_ability_table)
            print col
            device_port_ability = {}
            for dat in device_ability_table:
                for pa in port_ability:
                    if dat.split('.')[1].split()[0] == pa:
                        for sm in solution['module']:
                            if dat.split()[1] == sm['role']:
                                device_port_ability[pa] = {}
                                device_port_ability[pa]['module'] = sm['module']
                                device_port_ability[pa]['role'] = sm['role']
            device_solution['port'] = device_port_ability
            device_solution['chassis'] = solution['chassis']
        sql = "select device_slot,slot_model,slot_type from device_ability where model_name = '%s' and slot_type <> 'module' and slot_type <> 'linecard'"%device_solution['chassis']
        result_device = ndb.getdata(sql)
        result_device_type = set([ rd[2] for rd in result_device ])
        for rdt in result_device_type:
            device_ability_table = {}
            n = 1
            col = PrettyTable()
            for rdi in result_device:
                if rdi[2] == rdt:
                    device_ability_table[rdi[0]] = []
                    for rdj in  rdi[1].split(','):
                        device_ability_table[rdi[0]].append('%s.%s'%(str(n),rdj))
                        n += 1
                    col.add_column(rdi[2]+':'+rdi[0],device_ability_table[rdi[0]])
            print col
            print 'please select %s for each slot:'%rdt
            input_slot_list = []
            while True:
                device_slot = raw_input()
                input_slot_list = getnum(device_slot)
                a = 1
                for dat in device_ability_table:
                    if len([j for j in [ datd.split('.')[0] for datd in device_ability_table[dat] ] if j in input_slot_list]) > 1:
                        print 'one slot only need less more than one %s'%rdt
                        break
                    a = 0
                if a == 0:
                    break
            device_solution[rdt] = {}
            for dat in device_ability_table:
                for datd in device_ability_table[dat]:
                    for isl in input_slot_list:
                        if datd.split('.')[0] == isl:
                            device_solution[rdt][dat] = datd.split('.')[1]
        with open(hardware_version+'/'+role['role_name'],'w') as f:
            f.write(str(device_solution))
#        arch_conn += [ {'role_name':role['role_name'],'peer_role_name':rpr['peer_role_name'],'role_num':role['role_num'],'peer_role_num':rpr['peer_role_num']} for rpr in role['peer_role'] ]
        arch_conn += [{'role_name':role['role_name'],'role_num':role['role_num'],'peer_roles':[ {'peer_role_name':rpr['peer_role_name'],'peer_role_num':rpr['peer_role_num']} for rpr in role['peer_role']]}]
    with open(hardware_version+'/arch_conn','w') as f:
        f.write(str(arch_conn))
    return hardware_version



#更具硬件架构方案生成采购清单和连接关系        
def calculateorder(hardware_version):
    dbuser = databaseuser
    dbpass = databasepassword
    dbname = database
    dbhost = databasehost
    ndb = newdb(dbuser,dbpass,dbname,dbhost)
    try:
        arch_role_list = os.listdir(hardware_version+'/')
    except:
        print u'没有这个硬件版本文件夹！'
        sys.exit()
    remove_list = [ arl for arl in arch_role_list if 'order_scheme' in arl or 'arch_conn' in arl ]
    for rl in remove_list:
        arch_role_list.remove(rl)
    arch_role = {}
    with open(hardware_version+'/arch_conn','r') as f:
        arch_conn_cmd = f.read()
    cmd = "arch_conn_table = %s"%arch_conn_cmd
    exec(cmd) in locals()
    arch_conn = []
    for act in arch_conn_table:
        arch_conn += [ {'role_name':act['role_name'],'peer_role_name':apr['peer_role_name'],'role_num':act['role_num'],'peer_role_num':apr['peer_role_num']} for apr in act['peer_roles'] ]
    for role in arch_role_list:
        with open(hardware_version+'/'+role,'r') as f:
            arch_solution = f.read()
        cmd = "arch_role['%s']=%s"%(role,arch_solution)
        exec(cmd) in locals()
    link_table = []
    for ac in arch_conn:
        conn_table = []
        local_role_name = ac['role_name']
        local_role_num = ac['role_num']
        peer_role_name = ac['peer_role_name']
        peer_role_num = ac['peer_role_num']
        local_port_list = deviceintsort([ alp for alp,alpt in arch_role[local_role_name]['port'].items() if alpt['role'] == peer_role_name])
        local_device_name = [ local_role_name+str(rl) for rl in range(1,int(local_role_num)+1)]
        peer_device_name = [ peer_role_name+str(rl) for rl in range(1,int(peer_role_num)+1)]
        if peer_role_name == local_role_name:
            for n in [2*i for i in range(len(local_device_name)/2)]:
                for lpl in local_port_list:
                    conn_table.append([local_device_name[n],lpl,local_device_name[n+1],lpl])
            link_table += conn_table
            continue
        peer_role_num_n = peer_role_num
        if peer_role_name in arch_role_list:
            peer_port_list = deviceintsort([ alp for alp,alpt in arch_role[peer_role_name]['port'].items() if alpt['role'] == local_role_name])
            arch_conn_element =[ ace for ace in arch_conn if ace['peer_role_name'] == local_role_name and ace['role_name'] == peer_role_name ][0]
            peer_role_num_n = arch_conn_element['role_num']
            peer_device_name = [ peer_role_name+str(rl) for rl in range(1,int(peer_role_num_n)+1)]
            arch_conn.remove(arch_conn_element)
        else:
            peer_port_list = ['' for i in range(int(len(local_port_list)*int(local_role_num)/int(peer_role_num_n)))]
        if int(peer_role_num_n) > int(local_role_num):
            if len(peer_port_list)*int(peer_role_num_n) > len(local_port_list)*int(local_role_num):
                print 'the ports num of %s is not equal for %s,please replan the arch solution'%(local_role_name,peer_role_name)
                conn_table = []
                break
            elif len(peer_port_list)*int(peer_role_num_n) < len(local_port_list)*int(local_role_num):
                n = 0 if len(peer_port_list)*int(peer_role_num_n)%int(local_role_num) == 0 else 1
                local_port_list = local_port_list[:len(peer_port_list)*int(peer_role_num_n)/int(local_role_num)+n]
        elif int(peer_role_num_n) < int(local_role_num):
            if len(peer_port_list)*int(peer_role_num_n) < len(local_port_list)*int(local_role_num):
                print 'the ports num of %s is not equal for %s,please replan the arch solution'%(peer_role_name,local_role_name)
                conn_table = []
                break
            elif len(peer_port_list)*int(peer_role_num_n) > len(local_port_list)*int(local_role_num):
                n = 0 if len(local_port_list)*int(local_role_num)%int(peer_role_num_n) == 0 else 1
                peer_port_list = peer_port_list[:len(local_port_list)*int(local_role_num)/int(peer_role_num_n)+n]
        else:
            if len(peer_port_list)*int(peer_role_num_n) != len(local_port_list)*int(local_role_num):
                print 'the ports num of %s and %s for each other are not equal,please replan the arch solution'%(peer_role_name,local_role_name)
                conn_table = []
                break
        for ldn in local_device_name:
            for lpl in local_port_list:
                conn_table.append([ldn,lpl,'',''])
        peer_port_dict = {}
        for pdn in  peer_device_name:
            peer_port_dict[pdn] = copy.copy(peer_port_list)
        n = 0
        m = 0
        pnum = len(local_port_list)/int(peer_role_num)
        while  n < len(conn_table):
            pdn = peer_device_name[m%int(peer_role_num_n)]
            m += 1
            a_n = 0
            while a_n < pnum:
                conn_table[n][2] = pdn
                conn_table[n][3] = peer_port_dict[pdn].pop(0)
                n += 1 
                a_n += 1
        link_table += conn_table
    device_list = []
    for act in arch_conn_table:
        print u'请输入本次要建设%s的设备序号，默认是全建'%act['role_name']
        print 'please input %s num,default is 1-%s :'%(act['role_name'],act['role_num'])
        num = raw_input()
        arch_num = getnum(num)
        all_num = [ an for an in arch_num if int(an) in range(1,int(act['role_num'])+1) ]
        if all_num == []:
            all_num = range(1,int(act['role_num'])+1)
        device_list +=  [act['role_name']+str(an) for an in all_num]
    last_link_table = []
    for lt in link_table:
        if lt[0] not in device_list and lt[2] not in device_list:
            continue
        elif lt[0] not in device_list and lt[1] != '':
            continue
        elif lt[2] not in device_list and lt[3] != '':
            continue
        else:
            last_link_table.append(lt)
    device_ability_list = {}
    for dl in device_list:
        device_ability_list[dl] = {}
        role = re.sub('\d','',dl)
        linecard_num = [ arch_role[role]['port'][llt[1]]['linecard_num'] for llt in last_link_table if llt[0] == dl and arch_role[role]['port'][llt[1]].has_key('linecard_num')]
        linecard_num += [ arch_role[role]['port'][llt[3]]['linecard_num'] for llt in last_link_table if llt[2] == dl and arch_role[role]['port'][llt[3]].has_key('linecard_num')]
        linecard_num = set(linecard_num)
        if linecard_num != []:
            device_ability_list[dl]['linecard'] = {}
            for ln in linecard_num:
                device_ability_list[dl]['linecard'][ln] = arch_role[role]['linecard'][ln]
        port_num = [ llt[1] for llt in last_link_table if llt[0] == dl ]
        port_num += [ llt[3] for llt in last_link_table if llt[2] == dl ]
        if port_num != []:
            device_ability_list[dl]['module'] = {}
            for pn in port_num:
                device_ability_list[dl]['module'][pn] = arch_role[role]['port'][pn]['module']
        for ar in arch_role[role]:
            if ar != 'port' and ar != 'linecard':
                device_ability_list[dl][ar] = arch_role[role][ar]
    device_type_dict = {'module':u'模块','linecard':u'板卡','fabriccard':u'交换网板','fan':u'风扇','power':u'电源','chassis':u'机框','monitoring':u'监控板','supervisor':u'引擎板'}
    order_list = []
    for dal in device_ability_list:
        for dald in device_ability_list[dal]:
            if dald == 'chassis':
                order_list.append(device_ability_list[dal]['chassis'])
            else:
                for daldv in device_ability_list[dal][dald].values():
                    order_list.append(daldv)
    order_type  = set(order_list)
    order_dict = {}
    for ot in order_type:
        order_dict[ot] = order_list.count(ot)
    module_dict = {}
    for od in order_dict:
        sql = "select device_type,module_connectortype from device_information where model_name = '%s'"%od
        result_type = ndb.getdata(sql)
        if result_type != () :  
            if result_type[0][0] == 'module':
                module_dict[od]=result_type[0][1] 
    link_order = {}
    link_type_set = set([ re.sub('\d','',llt[0])+'-'+re.sub('\d','',llt[2]) for llt in last_link_table ])
    for lts in link_type_set:
        link_order[lts] = []
    for llt in last_link_table:
        a_device_type = re.sub('\d','',llt[0])
        a_port = llt[1]
        b_device_type = re.sub('\d','',llt[2])
        b_port = llt[3]
        link_device_type = a_device_type + '-' + b_device_type
        if a_port != '':
            a_module = arch_role[a_device_type]['port'][a_port]['module']
        else:
            a_module = ''
        if b_port != '':
            b_module = arch_role[b_device_type]['port'][b_port]['module']
        else:
            b_module = ''
        if a_module == '':
            a_module = b_module
        if b_module == '':
            b_module = a_module
        a_link_type = module_dict[a_module]
        b_link_type = module_dict[b_module]
        link_type = a_link_type+'-'+b_link_type
        llt.append(link_type)
        llt.insert(0,link_device_type)
        link_order[link_device_type].append(link_type)
    link_odrder_dict = {}
    for lo in link_order:
        link_odrder_dict[lo] = {}
        for slol in set([ lol for lol in  link_order[lo]]):
            link_odrder_dict[lo][slol] = link_order[lo].count(slol)
    style = xlwt.XFStyle()
    al = xlwt.Alignment()
    al.horz = 0x02
    al.vert = 0x01
    style.alignment = al
    font = xlwt.Font()
    font.name = 'title'
    font.bold = True
    style.font = font
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40 
    style.borders = borders
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 5
    style.pattern = pattern
    style1 = xlwt.XFStyle()
    al = xlwt.Alignment()
    al.horz = 0x02
    al.vert = 0x01
    style1.alignment = al
    font = xlwt.Font()
    font.name = 'paper'
    font.bold = True
    style1.font = font
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40 
    style1.borders = borders
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u'物料清单',cell_overwrite_ok=True)
    row0 = [u'型号',u'类型',u'厂商',u'数量']
    for i in range(0,len(row0)):
        sheet1.write(0,i,row0[i],style)
        sheet1.col(i).width = 3500
    n = 1
    for od in order_dict:
        sql = "select device_type,device_vendor from device_information where model_name = '%s'"%od
        result_type = ndb.getdata(sql)
        try:
            device_vendor = result_type[0][1]
            device_type = device_type_dict[result_type[0][0]]
        except:
            device_vendor = ''
            device_type = ''
        sheet1.write(n,0,od,style1)
        sheet1.write(n,1,device_type,style1)
        sheet1.write(n,2,device_vendor,style1)
        sheet1.write(n,3,order_dict[od],style1)
        n += 1
    row0 = [u'设备连接类型',u'线缆类型',u'数量']
    for i in range(0,len(row0)):
        sheet1.write(0,i+5,row0[i],style)
        sheet1.col(i).width = 3500
    n = 1
    for lod in link_odrder_dict:
        for lodl,lodlt in link_odrder_dict[lod].items():
            sheet1.write(n,5,lod,style1)
            sheet1.write(n,6,lodl,style1)
            sheet1.write(n,7,lodlt,style1)
            n += 1
    sheet2 = f.add_sheet(u'连接关系',cell_overwrite_ok=True)
    row1 = [u'连接类型',u'本端设备',u'本端设备端口',u'对端设备',u'对端设备接口',u'线缆类型']
    for i in range(0,len(row1)):
        sheet2.write(0,i,row1[i],style)
        sheet2.col(i).width = 3500
    n = 1
    for llt in last_link_table:
        for i in range(len(llt)):
            sheet2.write(n,i,llt[i],style1)
        n += 1
    sheet3 = f.add_sheet(u'物料安装表',cell_overwrite_ok=True)
    row2 = [u'设备',u'物料',u'类型',u'槽位']
    for i in range(0,len(row2)):
        sheet3.write(0,i,row2[i],style)
        sheet3.col(i).width = 3500
    n = 1
    for dl in device_list:
        for dal in device_ability_list[dl]:
            if dal == 'chassis':
                sheet3.write(n,0,dl,style1)
                sheet3.write(n,1,device_ability_list[dl][dal],style1)
                sheet3.write(n,2,device_type_dict[dal],style1)
                sheet3.write(n,3,'',style1)
                n += 1
            else:
                for dald,daldi in device_ability_list[dl][dal].items():
                    sheet3.write(n,0,dl,style1)
                    sheet3.write(n,1,daldi,style1) 
                    sheet3.write(n,2,device_type_dict[dal],style1)
                    sheet3.write(n,3,dald,style1)
                    n += 1
    filename = 'order_scheme_%s.xls'%time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))
    f.save(hardware_version+'/'+filename)



if __name__ == '__main__':
    if len(sys.argv) == 1:
        planfile = buildplanfile()
        hardware_version = calculatescheme(planfile)
        calculateorder(hardware_version)
    elif sys.argv[1] == '-c':
        if len(sys.argv) == 3:
            hardware_version = calculatescheme(sys.argv[2].strip())
            calculateorder(hardware_version)
        else:
            planfile = buildplanfile()
            hardware_version = calculatescheme(planfile)
            calculateorder(hardware_version)
    elif sys.argv[1] == '-if':
        if len(sys.argv) == 3:
            insertdeviceinfo(sys.argv[2])
        else:
            print u'请指定正确的导入文件'
    elif sys.argv[1] == '-ia':
        if len(sys.argv) == 3:
            insertdeviceability(sys.argv[2])
        else:
            print u'请指定正确的导入文件'
    elif sys.argv[1] == '-ca':
        if len(sys.argv) == 3:
            hardware_version = sys.argv[2].strip()
            calculateorder(hardware_version)
    else:
        help()
