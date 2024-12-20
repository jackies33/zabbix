



from netmiko import ConnectHandler, NetmikoAuthenticationException
import re


from map_manager.device_types.connect_prep import CONNECT_PREPARE


class B4COM_CONN():
    """
    Class for connection to different device
    """

    def __init__(self, **kwargs):
        """
        Initialize the values
        """
        self.pattern_lldp_b4com_main = re.compile(r'''
            ^(?P<local_interface>\S+)                 # Локальный интерфейс
            \s+(?P<device_id>[\S+]+\s*)                  # Имя устройства
            (?P<mac_address>(?:[0-9a-f]{4}\.){2}[0-9a-f]{4})  # MAC-адрес
            \s+(?P<port_id>\S+)                       # Удаленный порт
        ''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)
        self.pattern_lldp_b4com_CS2148 = re.compile(r'''
            Local\s+Port\s+:\s+(?P<local_interface>\S+)\n      # Локальный интерфейс
            Remote\s+Port\s+:\s+(?P<port_id>\S+)\n   # Удаленный порт
            (?:.*\n)*? 
            System\s+Name\s+:\s+(?P<device_id>\S+)     # Имя устройства
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
        elif re.match(r"XGE\d+", iface):
            iface = iface.replace("XGE", "XGigabitEthernet")
        return iface

    def conn_B4COM_main(self, **kwargs):
        print("<<< Start b4com.py >>>")
        host_name = kwargs['name']
        try:
            my_lldp = []
            device_type_template = '1'
            group_device_type = kwargs['groups']
            if group_device_type: #try to find out another type of device, if True it will be another way to find LLDP neighbours
                group_device_type =group_device_type[0]['name']
                device_type = group_device_type.split('/')[-1]
                if device_type == "CS2148P" or device_type == "CS2148T":
                    device_type_template = '2'
                    #result = self.conn_B4COM_CS2148(**kwargs)
                    #return result
            ip_conn = kwargs['interfaces'][0]['ip']
            host_name = kwargs['name']
            #group = kwargs['groups'][0]['name']
            type_device_for_conn = "b4com"
            dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                 'conn_scheme': '2'}
            template = CONNECT_PREPARE()
            host1 = template.template_conn(**dict_for_template)
        except Exception as err:
            print(err)
            return [False, None, host_name]
        try:
            with ConnectHandler(**host1) as net_connect:
                if device_type_template == '1':
                    output_main = net_connect.send_command('show lldp neighbors', delay_factor=.5)
                    matches = self.pattern_lldp_b4com_main.finditer(output_main)
                    for match in matches:
                        remote_sysname = match.group('device_id').strip()
                        if remote_sysname != None:
                            if "\n" in remote_sysname:
                                remote_sysname = remote_sysname.split("\n")[1]
                            if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                            if ".tech" in str(remote_sysname):
                                remote_sysname = remote_sysname.split(".tech")[0]
                        local_iface = match.group('local_interface')
                        if local_iface != None:
                            local_iface = self.iface_correcting(local_iface)
                        remote_iface = match.group('port_id')
                        if remote_iface != None:
                            remote_iface = self.iface_correcting(remote_iface)
                        if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                            for id in self.scale_ids_with_names_for_ibm:
                                if str(id["port_id"]) == remote_iface:
                                    try:
                                        remote_iface = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        if local_iface != None and remote_iface != None and remote_sysname != None:
                            my_lldp.append({local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                elif device_type_template == '2':
                    output_main = net_connect.send_command('show lldp neighbor brief', delay_factor=.5)
                    matches = self.pattern_lldp_b4com_CS2148.finditer(output_main)
                    for match in matches:
                        remote_sysname = match.group('device_id').strip()
                        if remote_sysname != None:
                            if "\n" in remote_sysname:
                                remote_sysname = remote_sysname.split("\n")[1]
                            if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                            if ".tech" in str(remote_sysname):
                                remote_sysname = remote_sysname.split(".tech")[0]
                        local_iface = match.group('local_interface')
                        if local_iface != None:
                            local_iface = self.iface_correcting(local_iface)
                        remote_iface = match.group('port_id')
                        if remote_iface != None:
                            remote_iface = self.iface_correcting(remote_iface)
                        if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                            for id in self.scale_ids_with_names_for_ibm:
                                if str(id["port_id"]) == remote_iface:
                                    try:
                                        remote_iface = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        if local_iface != None and remote_iface != None and remote_sysname != None:
                            my_lldp.append(
                                {local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
            lldp_dict = {"local_hostname": host_name, "lldp_list": my_lldp, "zbx_data": kwargs}
            net_connect.disconnect()
            return [True, lldp_dict]
        except NetmikoAuthenticationException as err:
            print(err)
            dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                 'conn_scheme': '2'}
            template = CONNECT_PREPARE()
            host1 = template.template_conn_reserve(**dict_for_template)
            try:
                with ConnectHandler(**host1) as net_connect:
                    print(device_type_template)
                    if device_type_template == '1':
                        output_main = net_connect.send_command('show lldp neighbors', delay_factor=.5)
                        matches = self.pattern_lldp_b4com_main.finditer(output_main)
                        for match in matches:
                            remote_sysname = match.group('device_id').strip()
                            if remote_sysname != None:
                                if "\n" in remote_sysname:
                                    remote_sysname = remote_sysname.split("\n")[1]
                                if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                    remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                                if ".tech" in str(remote_sysname):
                                    remote_sysname = remote_sysname.split(".tech")[0]
                            local_iface = match.group('local_interface')
                            if local_iface != None:
                                local_iface = self.iface_correcting(local_iface)
                            remote_iface = match.group('port_id')
                            if remote_iface != None:
                                remote_iface = self.iface_correcting(remote_iface)
                            if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                                for id in self.scale_ids_with_names_for_ibm:
                                    if str(id["port_id"]) == remote_iface:
                                        try:
                                            remote_iface = str(id["port_name"])
                                        except Exception as err:
                                            pass
                            if local_iface != None and remote_iface != None and remote_sysname != None:
                                my_lldp.append(
                                    {local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                    elif device_type_template == '2':
                        output_main = net_connect.send_command('show lldp neighbor brief', delay_factor=.5)
                        matches = self.pattern_lldp_b4com_CS2148.finditer(output_main)
                        for match in matches:
                            remote_sysname = match.group('device_id').strip()
                            if remote_sysname != None:
                                if "\n" in remote_sysname:
                                    remote_sysname = remote_sysname.split("\n")[1]
                                if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                    remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                                if ".tech" in str(remote_sysname):
                                    remote_sysname = remote_sysname.split(".tech")[0]
                            local_iface = match.group('local_interface')
                            if local_iface != None:
                                local_iface = self.iface_correcting(local_iface)
                            remote_iface = match.group('port_id')
                            if remote_iface != None:
                                remote_iface = self.iface_correcting(remote_iface)
                            if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                                for id in self.scale_ids_with_names_for_ibm:
                                    if str(id["port_id"]) == remote_iface:
                                        try:
                                            remote_iface = str(id["port_name"])
                                        except Exception as err:
                                            pass
                            if local_iface != None and remote_iface != None and remote_sysname != None:
                                my_lldp.append(
                                    {local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                lldp_dict = {"local_hostname": host_name, "lldp_list": my_lldp, "zbx_data": kwargs}
                net_connect.disconnect()
                return [True, lldp_dict]
            except Exception as err:
                print(err)
                return [False, None, host_name]
        except Exception as err:
            print(err)
            return [False, None, host_name]





#if __name__ == "__main__":
#    connecting = B4COM_CONN()
#    my_dict = {'local_hostname': 'adm2-mgmt-asw-h23',  'interfaces': [{'ip': '100.64.0.223'}], "name":'adm2-mgmt-asw-h23',
#               'groups': [{'groupid': '126', 'name': 'B4COM/B4TECH/CS2148P'}]
#               }
#    result = connecting.conn_B4COM_main(**my_dict)
#    print(result)



