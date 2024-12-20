


import re
import time
import paramiko

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))
from map_manager.my_env import mylogin , mypass



class IBM():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """
                self.mac_regex = re.compile(r'([0-9A-Fa-f]{2}([-:]?)){5}[0-9A-Fa-f]{2}')
                self.rx_lldp = re.compile(
                    r"^(?P<local_iface>\S+)\s+\|\s+\d+\s+\|\s+(?P<remote_id>\S+|.{17})"
                    r"\s+\|\s(?P<remote_iface>\S+)\s+\|\s+(?P<remote_sysname>\S+)\s*\|",
                    re.MULTILINE,
                )
                self.scale_ids_with_names = [{"snmp_id": 129,"port_name":"INTA1", "port_id": 1}, {"snmp_id": 130,"port_name":"INTA2", "port_id": 2},
             {"snmp_id": 131,"port_name":"INTA3", "port_id": 3}, {"snmp_id": 132,"port_name":"INTA4", "port_id": 4},
             {"snmp_id": 133,"port_name":"INTA5", "port_id": 5}, {"snmp_id": 134,"port_name":"INTA6", "port_id": 6},
             {"snmp_id": 135,"port_name":"INTA7", "port_id": 7}, {"snmp_id": 136,"port_name":"INTA8", "port_id": 8},
             {"snmp_id": 137,"port_name":"INTA9", "port_id": 9}, {"snmp_id": 138,"port_name":"INTA10", "port_id": 10},
             {"snmp_id": 139,"port_name":"INTA11", "port_id": 11}, {"snmp_id": 140,"port_name":"INTA12", "port_id": 12},
             {"snmp_id": 141,"port_name":"INTA13", "port_id": 13}, {"snmp_id": 142,"port_name":"INTA14", "port_id": 14},
             {"snmp_id": 143, "port_id": 15}, {"snmp_id": 144, "port_id": 16},
             {"snmp_id": 145, "port_id": 17}, {"snmp_id": 146, "port_id": 18},
             {"snmp_id": 147, "port_id": 19}, {"snmp_id": 148, "port_id": 20},
             {"snmp_id": 149, "port_id": 21}, {"snmp_id": 150, "port_id": 22},
             {"snmp_id": 151, "port_id": 23}, {"snmp_id": 152, "port_id": 24},
             {"snmp_id": 153, "port_id": 25}, {"snmp_id": 154, "port_id": 26},
             {"snmp_id": 155, "port_id": 27}, {"snmp_id": 156, "port_id": 28},
             {"snmp_id": 171, "port_name":"EXT1", "port_id": 43}, {"snmp_id": 172, "port_name":"EXT2", "port_id": 44},
             {"snmp_id": 173, "port_name":"EXT3", "port_id": 45}, {"snmp_id": 174, "port_name":"EXT4", "port_id": 46},
             {"snmp_id": 175, "port_name":"EXT5", "port_id": 47}, {"snmp_id": 176, "port_name":"EXT6", "port_id": 48},
             {"snmp_id": 177, "port_name":"EXT7", "port_id": 49}, {"snmp_id": 178, "port_name":"EXT8", "port_id": 50},
             {"snmp_id": 179, "port_name":"EXT9", "port_id": 51}, {"snmp_id": 180, "port_name":"EXT10", "port_id": 52},
             {"snmp_id": 185, "port_id": 57}, {"snmp_id": 186, "port_id": 58},
             {"snmp_id": 187, "port_id": 59}, {"snmp_id": 188, "port_id": 60},
             {"snmp_id": 189, "port_id": 61}, {"snmp_id": 190, "port_id": 62},
             {"snmp_id": 191, "port_id": 63}, {"snmp_id": 192, "port_id": 64},
             {"snmp_id": 193, "port_name":"EXTM", "port_id": 65}, {"snmp_id": 194, "port_name":"MGT1", "port_id": 66}]

            def iface_correcting(self, iface):
                if re.match(r"Gi\d+", iface):
                    iface = iface.replace("Gi", "GigabitEthernet")
                elif re.match(r"Te\d+", iface):
                    iface = iface.replace("Te", "TenGigabitEthernet")
                elif re.match(r"Fa\d+", iface):
                    iface = iface.replace("Fa", "FastEthernet")
                elif re.match(r"Eth\d+", iface):
                    iface = iface.replace("Eth", "Ethernet")
                elif re.match(r"XGE\d+", iface):
                    iface = iface.replace("XGE", "XGigabitEthernet")
                return iface


            def conn_IBM_lenovo_sw(self ,**kwargs):
                print("<<< Start ibm.py >>>")
                my_lldp = []
                try:
                    ip_conn = kwargs['interfaces'][0]['ip']
                    host_name = kwargs['name']
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    cmnd1 = '\nshow lldp remote-device    \n\n\n\n     '
                    ssh.connect(ip_conn,
                                username=mylogin,
                                password=mypass,
                                look_for_keys=False,
                                allow_agent=False)
                    ssh1 = ssh.invoke_shell()
                    time.sleep(1)
                    ssh1.send(cmnd1)
                    time.sleep(1)
                    output_main_result = (ssh1.recv(65535).decode("utf-8"))
                    #print(output_main_result)
                    matches = self.rx_lldp.finditer(output_main_result)
                    for match in matches:
                        local_iface = match.group('local_iface')
                        remote_iface = match.group('remote_iface')
                        checking_lenovo_port = re.match(r"^\d{2}$", remote_iface)
                        if checking_lenovo_port != None:
                            for id in self.scale_ids_with_names:
                                if str(id["port_id"]) == remote_iface:
                                    try:
                                        remote_iface = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        if remote_iface != None:
                            remote_iface = self.iface_correcting(remote_iface)
                        remote_sysname = match.group('remote_sysname')
                        if remote_sysname != None:
                            if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                        if local_iface != None and remote_iface != None and remote_sysname != None and not self.mac_regex.match(remote_iface):
                            my_lldp.append(
                                {local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                    ssh1.close()
                    lldp_dict = {"local_hostname": host_name, "lldp_list": my_lldp, "zbx_data": kwargs}
                    return [True, lldp_dict]
                except Exception as err:
                    print(err)
                    return [False, None, host_name]





