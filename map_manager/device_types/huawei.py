



from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException, ReadException
import re


import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.device_types.connect_prep import CONNECT_PREPARE


class HUAWEI_CONN():
    """
    Class for connection to different device
    """

    def __init__(self):
        """
        Initialize the values
        """
        self.neigh_pattern_common = re.compile(r"""
                            (?P<local_iface>GigabitEthernet[^\s]+|XGigabitEthernet[^\s]+|25GE[^\s]+|100GE[^\s]+|10GE[^\s]+|MEth[^\s]+) \s+      # Локальный интерфейс
                            (?P<remote_hostname>[^\s]+) \s+                                           # Имя соседнего устройства
                            (?P<remote_iface>\S+[^\s]+)        # Интерфейс на соседнем устройстве
                         
                        """, re.VERBOSE)
        self.neigh_pattern_excluding = re.compile(r"""
                            (?P<local_iface>GigabitEthernet[^\s]+|XGigabitEthernet[^\s]+|25GE[^\s]+|100GE[^\s]+|10GE[^\s]+|MEth[^\s]+) \s+\d+\s+      # Локальный интерфейс
                            (?P<remote_iface>\S+[^\s]+) \s+
                            (?P<remote_hostname>[^\s]+)                                     
                        """, re.VERBOSE)
        self.diff_pattern_devices = ["Huawei Technologies Co./Huawei.VRP/CE6881-48S6CQ","Huawei Technologies Co./Huawei.VRP/CE8851-32CQ8DQ-P"]
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

    def conn_Huawei(self, **kwargs):
        print("<<< Start huawei.py >>>")
        host_name = kwargs['name']
        try:
            ip_conn = kwargs['interfaces'][0]['ip']
            type_device_for_conn = 'huawei'
            dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn, 'conn_scheme': '2'}
            template = CONNECT_PREPARE()
            host1 = template.template_conn(**dict_for_template)
            print("<<< Start huawei.py >>>")
            try:
                with ConnectHandler(**host1) as net_connect:
                    output_lldp_main_result = net_connect.send_command('display lldp neighbor brief', delay_factor=0.5)
                    group = kwargs['groups'][0]['name']
                    for group_name_diff in self.diff_pattern_devices:
                        if group_name_diff == group:
                            matches = self.neigh_pattern_excluding.finditer(output_lldp_main_result)
                            break
                        else:
                            matches = self.neigh_pattern_common.finditer(output_lldp_main_result)
                    lldp_list = []
                    for match in matches:
                        data = match.groupdict()
                        interface = data.pop('local_iface')
                        remote_sysname = data.pop('remote_hostname')
                        if remote_sysname != None:
                            if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                        remote_iface = data.pop('remote_iface')
                        if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                            for id in self.scale_ids_with_names_for_ibm:
                                if str(id["port_id"]) == remote_iface:
                                    try:
                                        remote_iface = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        if remote_iface != None:
                            remote_iface = self.iface_correcting(remote_iface)
                        lldp_list.append({interface: {"remote_hostname": remote_sysname, 'remote_iface': remote_iface}})
                    lldp_dict = {"local_hostname": host_name, "lldp_list": lldp_list, "zbx_data": kwargs}
                    net_connect.disconnect()
                    return [True, lldp_dict]
            except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                print('\n\n not connect to ' + ip_conn + '\n\n')
                return [False, err, host_name]
        except Exception as err:
            print(err)
            return [False, err, host_name]

#host = {'hostid': '12891', 'name': 'chernogolovka-ar01', 'parentTemplates': [{'templateid': '16225', 'name': 'Huawei VRP p-pe'}], 'groups': [{'groupid': '32', 'name': 'Huawei Technologies Co./Huawei.VRP/NE20E-S2F'}], 'interfaces': [{'ip': '10.100.138.60'}], 'tags': [{'tag': 'remote_id', 'value': '1248', 'automatic': '0'}, {'tag': 'Connection_Scheme', 'value': 'ssh', 'automatic': '0'}, {'tag': 'MAP_Group', 'value': 'MAP_Group_MUS', 'automatic': '0'}, {'tag': 'Name_of_Establishment', 'value': 'None', 'automatic': '0'}, {'tag': 'TG_Group', 'value': 'TG_Group_MOCIKT_Main', 'automatic': '0'}, {'tag': 'mac_address', 'value': 'None', 'automatic': '0'}, {'tag': 'device_role', 'value': 'p-pe', 'automatic': '0'}, {'tag': 'tenant', 'value': 'ЕИМТС', 'automatic': '0'}]}


#call = HUAWEI_CONN()
#result = call.conn_Huawei(**host)
#print(result)


