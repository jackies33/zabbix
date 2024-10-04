



import re
import time
import paramiko

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.my_env import mylogin , mypass



class FORTINET_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """
                self.pattern_forti = re.compile(r'''
                                                ^\d+\s+port\s+(?P<local_iface>'\S+')     
                                                .+port\s+(?P<remote_iface>'\S+')
                                                \s+system\s+(?P<remote_sysname>'\S+')
                                            ''', re.VERBOSE | re.MULTILINE)
                self.scale_ids_with_names_for_ibm = [{"snmp_id": 129, "port_name": "INTA1", "port_id": 1},
                                                     {"snmp_id": 130, "port_name": "INTA2", "port_id": 2},
                                                     {"snmp_id": 131, "port_name": "INTA3", "port_id": 3},
                                                     {"snmp_id": 132, "port_name": "INTA4", "port_id": 4},
                                                     {"snmp_id": 133, "port_name": "INTA5", "port_id": 5},
                                                     {"snmp_id": 134, "port_name": "INTA6", "port_id": 6},
                                                     {"snmp_id": 135, "port_name": "INTA7", "port_id": 7},
                                                     {"snmp_id": 136, "port_name": "INTA8", "port_id": 8},
                                                     {"snmp_id": 137, "port_name": "INTA9", "port_id": 9},
                                                     {"snmp_id": 138, "port_name": "INTA10", "port_id": 10},
                                                     {"snmp_id": 139, "port_name": "INTA11", "port_id": 11},
                                                     {"snmp_id": 140, "port_name": "INTA12", "port_id": 12},
                                                     {"snmp_id": 141, "port_name": "INTA13", "port_id": 13},
                                                     {"snmp_id": 142, "port_name": "INTA14", "port_id": 14},
                                                     {"snmp_id": 143, "port_id": 15}, {"snmp_id": 144, "port_id": 16},
                                                     {"snmp_id": 145, "port_id": 17}, {"snmp_id": 146, "port_id": 18},
                                                     {"snmp_id": 147, "port_id": 19}, {"snmp_id": 148, "port_id": 20},
                                                     {"snmp_id": 149, "port_id": 21}, {"snmp_id": 150, "port_id": 22},
                                                     {"snmp_id": 151, "port_id": 23}, {"snmp_id": 152, "port_id": 24},
                                                     {"snmp_id": 153, "port_id": 25}, {"snmp_id": 154, "port_id": 26},
                                                     {"snmp_id": 155, "port_id": 27}, {"snmp_id": 156, "port_id": 28},
                                                     {"snmp_id": 171, "port_name": "EXT1", "port_id": 43},
                                                     {"snmp_id": 172, "port_name": "EXT2", "port_id": 44},
                                                     {"snmp_id": 173, "port_name": "EXT3", "port_id": 45},
                                                     {"snmp_id": 174, "port_name": "EXT4", "port_id": 46},
                                                     {"snmp_id": 175, "port_name": "EXT5", "port_id": 47},
                                                     {"snmp_id": 176, "port_name": "EXT6", "port_id": 48},
                                                     {"snmp_id": 177, "port_name": "EXT7", "port_id": 49},
                                                     {"snmp_id": 178, "port_name": "EXT8", "port_id": 50},
                                                     {"snmp_id": 179, "port_name": "EXT9", "port_id": 51},
                                                     {"snmp_id": 180, "port_name": "EXT10", "port_id": 52},
                                                     {"snmp_id": 185, "port_id": 57}, {"snmp_id": 186, "port_id": 58},
                                                     {"snmp_id": 187, "port_id": 59}, {"snmp_id": 188, "port_id": 60},
                                                     {"snmp_id": 189, "port_id": 61}, {"snmp_id": 190, "port_id": 62},
                                                     {"snmp_id": 191, "port_id": 63}, {"snmp_id": 192, "port_id": 64},
                                                     {"snmp_id": 193, "port_name": "EXTM", "port_id": 65},
                                                     {"snmp_id": 194, "port_name": "MGT1", "port_id": 66}]

            def iface_correcting(self, iface):
                if re.match(r"Gi\d+", iface):
                    iface = iface.replace("Gi", "GigabitEthernet")
                elif re.match(r"Te\d+", iface):
                    iface = iface.replace("Te", "TenGigabitEthernet")
                elif re.match(r"Fa\d+", iface):
                    iface = iface.replace("Fa", "FastEthernet")
                elif re.match(r"Eth\d+", iface):
                    iface = iface.replace("Eth", "Ethernet")
                return iface

            def conn_FortiGate_diagnose_lldprx(self, **kwargs):
                try:
                    print("<<< Start fortinet.py >>>")
                    my_lldp = []
                    group_name = kwargs['groups'][0]['name']
                    ip_conn = kwargs['interfaces'][0]['ip']
                    host_name = kwargs['name']
                    cmnd1_1for2500 = '\n config vdom \n\n      '  # Commands
                    cmnd1_2for2500 = '\n edit root \n\n      '  # Commands
                    cmnd1_1for6500 = '\n config global \n\n      '  # Commands
                    cmnd2 = '\n diagnose lldprx neighbor  \n\n           '  # Commands
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_conn,
                                username=mylogin,
                                password=mypass,
                                look_for_keys=False)
                    ssh1 = ssh.invoke_shell()
                    time.sleep(1)
                    if group_name == "Fortinet/Fortinet.Fortigate/FortiGate-6501F":
                        ssh1.send(cmnd1_1for6500)
                        time.sleep(1)
                        ssh1.send(cmnd2)
                        time.sleep(1)
                        time.sleep(1)
                    elif group_name == "Fortinet/Fortinet.Fortigate/FortiGate-2500E":
                        ssh1.send(cmnd1_1for2500)
                        time.sleep(1)
                        ssh1.send(cmnd1_2for2500)
                        time.sleep(1)
                        ssh1.send(cmnd2)
                        time.sleep(1)
                        time.sleep(1)
                    else:
                        return [False, "NOT proper group of hosts", host_name]
                    output1 = (ssh1.recv(9999999).decode("utf-8"))
                    matches = self.pattern_forti.finditer(output1)
                    for match in matches:
                        local_iface = match.group('local_iface')
                        if local_iface != None:
                            local_iface = local_iface.replace("'", "")
                        remote_iface = match.group('remote_iface')
                        if remote_iface != None:
                            remote_iface = self.iface_correcting(remote_iface.replace("'", ""))
                        if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                            for id in self.scale_ids_with_names_for_ibm:
                                if str(id["port_id"]) == remote_iface:
                                    try:
                                        remote_iface = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        remote_sysname = match.group('remote_sysname')
                        if remote_sysname != None:
                            remote_sysname = remote_sysname.replace("'", "")
                            if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                        if local_iface != None and remote_iface != None and remote_sysname != None:
                            my_lldp.append({local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                    lldp_dict = {"local_hostname": host_name, "lldp_list": my_lldp, "zbx_data": kwargs}
                    return [True, lldp_dict]
                except Exception as err:
                    print(err)
                    return [False, None, host_name]



            def FortiNet_start(self,**kwargs):
                group_name = kwargs['groups'][0]['name']
                if group_name == "Fortinet/Fortinet.Fortigate/FortiGate-6501F" \
                        or group_name == "Fortinet/Fortinet.Fortigate/FortiGate-2500E":
                    result = self.conn_FortiGate_diagnose_lldprx(**kwargs)
                    return result
                else:
                    return [False, None, kwargs['name']]
                #elif group_name == "Fortinet/Fortinet.Fortigate/FortiGate-2500E":

