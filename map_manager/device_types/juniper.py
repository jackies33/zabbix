


import re
from lxml import etree
import xml.etree.ElementTree as ET
from jnpr.junos import Device
import paramiko
import time

import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.my_env import mylogin , mypass



class JUNIPER_CONN():


            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                    """
                    Initialize the values
                    """
                    self.mac_regex = re.compile(r'([0-9A-Fa-f]{2}([-:]?)){5}[0-9A-Fa-f]{2}')
                    self.local_iface_pattern = re.compile(r'^Local Interface\s+:\s+([^\s]+)', re.MULTILINE)
                    self.remote_port_id_pattern = re.compile(r'^Port ID\s+:\s+([^\s]+)', re.MULTILINE)
                    self.remote_system_name_pattern = re.compile(r'^System name\s+:\s+([^\s]+)', re.MULTILINE)
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

            def iface_correcting(self,iface):
                if re.match(r"Gi\d+", iface):
                    iface = iface.replace("Gi", "GigabitEthernet")
                elif re.match(r"Te\d+", iface):
                    iface = iface.replace("Te", "TenGigabitEthernet")
                elif re.match(r"Fa\d+", iface):
                    iface = iface.replace("Fa", "FastEthernet")
                elif re.match(r"Eth\d+", iface):
                    iface = iface.replace("Eth", "Ethernet")
                return iface

            def uniq_list(self,my_list):
                try:
                    unique_list = []
                    seen = set()

                    for d in my_list:

                        key, value = list(d.items())[0]
                        value_tuple = tuple(value.items())

                        if (key, value_tuple) not in seen:
                            unique_list.append(d)
                            seen.add((key, value_tuple))

                    return unique_list
                except Exception as err:
                    print(err)
                    return []

            def conn_Juniper_rpc(self, **kwargs):
                try:
                    print("<<< Start juniper.py >>>")
                    sys.stderr = open(os.devnull, 'w')
                    ###consider data for collect and return
                    ip_conn = kwargs['interfaces'][0]['ip']
                    host_name = kwargs['name']
                    dev = Device(host=ip_conn, user=mylogin, password=mypass,timeout=60)
                    dev.open()
                    lldp_info = dev.rpc.get_lldp_neighbors_information()
                    lldp_xml = etree.tostring(lldp_info, pretty_print=True).decode()
                    root = ET.fromstring(lldp_xml)
                    my_lldp = []

                    for neighbor in root.findall('lldp-neighbor-information'):
                        try:
                            local_iface = neighbor.find('lldp-local-port-id')
                            if local_iface is not None:
                                local_iface = str(local_iface.text)
                            else:
                               local_iface = 'N/A'
                            remote_iface = neighbor.find('lldp-remote-port-id')
                            if remote_iface is not None:
                                remote_iface = str(remote_iface.text)
                            else:
                                remote_iface = 'N/A'
                            if remote_iface != None:
                                remote_iface = self.iface_correcting(remote_iface)
                            if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                                for id in self.scale_ids_with_names_for_ibm:
                                    if str(id["port_id"]) == remote_iface:
                                        try:
                                            remote_iface = str(id["port_name"])
                                        except Exception as err:
                                            pass
                            remote_hostname = neighbor.find('lldp-remote-system-name')
                            if remote_hostname is not None:
                                remote_hostname = str(remote_hostname.text)
                            else:
                                remote_hostname = 'N/A'
                            if str(remote_hostname).endswith('.tech.mosreg.ru'):
                                remote_hostname = remote_hostname.replace('.tech.mosreg.ru', '')
                            lldp_parent_iface = neighbor.find('lldp-local-parent-interface-name')
                            if lldp_parent_iface is not None:
                                lldp_parent_iface = str(lldp_parent_iface.text)
                            else:
                                lldp_parent_iface = 'N/A'
                            # i need to find out how i can finf a remote_iface for swithces
                            #if lldp_parent_iface != 'N/A' or lldp_parent_iface != '-':
                            #    command = f'show lldp neighbors interface {local_iface}'
                            ##    cli_output = dev.cli(command, format='xml')
                            #    root = ET.fromstring(cli_output)
                            #    print(root)

                            if not self.mac_regex.match(remote_iface) or remote_hostname != 'N/A':
                                #print(f"Local Interface: {local_iface}, Remote Interface: {remote_iface}, Remote Hostname: {remote_hostname}")
                                my_lldp.append({local_iface:{"remote_iface":remote_iface,"remote_hostname":remote_hostname}})
                            elif not self.mac_regex.match(remote_iface) and remote_hostname != 'N/A':
                                #print(f"Local Interface: {local_iface}, Remote Interface: {remote_iface}, Remote Hostname: {remote_hostname}")
                                my_lldp.append({local_iface:{"remote_iface":remote_iface,"remote_hostname":remote_hostname}})
                        except AttributeError as err:
                            print(err)
                            continue
                        except TypeError as err:
                            print(err)
                            continue
                    sys.stderr = sys.__stderr__
                    dev.close()
                    lldp_dict = {"local_hostname": host_name, "lldp_list": my_lldp, "zbx_data": kwargs}
                    return [True,lldp_dict]
                except Exception as err:
                    return [False,err, host_name]

            def conn_Juniper_cli(self, **kwargs):
                try:
                    print("<<< Start juniper.py >>>")
                    sys.stderr = open(os.devnull, 'w')
                    ###consider data for collect and return
                    ip_conn = kwargs['interfaces'][0]['ip']
                    host_name = kwargs['name']
                    my_lldp = []
                    cmnd1 = '\nshow lldp neighbors     \n\n                           '
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_conn,
                                username=mylogin,
                                password=mypass,
                                look_for_keys=False,
                                )

                    ssh1 = ssh.invoke_shell()
                    # time.sleep(1)
                    ssh1.send(cmnd1)
                    time.sleep(1)
                    output1 = (ssh1.recv(9999999).decode("utf-8"))
                    time.sleep(1)
                    interfaces_all = re.findall(r"xe-\d+/\d+/\d+|ge-\d+/\d+/\d+|et-\d+/\d+/\d+", output1)
                    for iface in interfaces_all:
                        ssh1.send(f'\nshow lldp neighbors interface {iface}      \n\n                          ')
                        time.sleep(1)
                        output2 = (ssh1.recv(9999999).decode("utf-8"))
                        local_iface_pattern = re.compile(r'^Local Interface\s+:\s+([^\s]+)', re.MULTILINE)
                        remote_port_id_pattern = re.compile(r'^Port ID\s+:\s+([^\s]+)', re.MULTILINE)
                        remote_system_name_pattern = re.compile(r'^System name\s+:\s+([^\s]+)', re.MULTILINE)
                        local_iface = local_iface_pattern.search(output2)
                        remote_port_id = remote_port_id_pattern.search(output2)
                        remote_system_name = remote_system_name_pattern.search(output2)
                        local_iface = local_iface.group(1) if local_iface else None
                        if local_iface != None:
                            if '.0' in local_iface:
                                local_iface = local_iface.replace('.0', '')
                            remote_port_id = remote_port_id.group(1) if remote_port_id else None
                        if remote_port_id != None:
                            remote_port_id= self.iface_correcting(remote_port_id)
                        remote_system_name = remote_system_name.group(1) if remote_system_name else None
                        if remote_system_name != None:
                            if str(remote_system_name).endswith('.tech.mosreg.ru'):
                                remote_system_name = remote_system_name.replace('.tech.mosreg.ru', '')
                        if remote_port_id.isdigit() and len(remote_port_id) in [1, 2]:
                            for id in self.scale_ids_with_names_for_ibm:
                                if str(id["port_id"]) == remote_port_id:
                                    try:
                                        remote_port_id = str(id["port_name"])
                                    except Exception as err:
                                        pass
                        if local_iface != None and remote_port_id != None and remote_system_name != None:
                            my_lldp.append(
                                {local_iface: {"remote_iface": remote_port_id, "remote_hostname": remote_system_name}})
                    sys.stderr = sys.__stderr__
                    lldp_list_correct = self.uniq_list(my_lldp)
                    if lldp_list_correct != []:
                        lldp_dict = {"local_hostname": host_name, "lldp_list": lldp_list_correct, "zbx_data": kwargs}
                        return [True, lldp_dict]
                    else:
                        return [False,None, host_name]
                except Exception as e:
                    return [False, e, host_name]

            def conn_Juniper_cli_via_rpc(self,**kwargs):
                print("<<< Start juniper.py >>>")
                sys.stderr = open(os.devnull, 'w')
                ###consider data for collect and return
                ip_conn = kwargs['interfaces'][0]['ip']
                host_name = kwargs['name']
                my_lldp = []
                try:

                    dev = Device(host=ip_conn, user=mylogin, password=mypass, timeout=90)
                    dev.open()
                    lldp_info = dev.rpc.get_lldp_neighbors_information()
                    lldp_xml = etree.tostring(lldp_info, pretty_print=True).decode()
                    root = ET.fromstring(lldp_xml)
                    # print(lldp_xml)
                    for neighbor in root.findall('lldp-neighbor-information'):
                        local_iface = neighbor.find('lldp-local-port-id')
                        if local_iface is not None:
                            local_iface = str(local_iface.text)
                        elif local_iface == None:
                            local_iface = neighbor.find('lldp-local-interface')
                            if local_iface is not None:
                                local_iface = str(local_iface.text)
                        else:
                            local_iface = None
                        if local_iface != None:
                            if '.0' in local_iface:
                                local_iface = local_iface.replace('.0', '')
                            lldp_output = dev.cli(f'show lldp neighbors interface {local_iface}', format='xml')
                            #lldp_output = dev.rpc.get_lldp_interface_neighbors_information(interface_name=local_iface)
                            lldp_xml1 = etree.tostring(lldp_output, pretty_print=True).decode()
                            root1 = ET.fromstring(lldp_xml1)
                            parse1 = root1.find('lldp-neighbor-information')
                            remote_iface = parse1.find('lldp-remote-port-id')
                            if remote_iface != None:
                                remote_iface = str(remote_iface.text)
                                remote_iface = self.iface_correcting(remote_iface)
                            else:
                                try:
                                    parse2 = root1.findall('lldp-neighbor-information')[1]
                                    remote_iface = parse2.find('lldp-remote-port-id')
                                    if remote_iface != None:
                                        remote_iface = str(remote_iface.text)
                                except Exception as err:
                                    print(err)
                                    remote_iface = None
                            if remote_iface != None:
                                remote_iface = self.iface_correcting(remote_iface)
                            if remote_iface.isdigit() and len(remote_iface) in [1, 2]:
                                for id in self.scale_ids_with_names_for_ibm:
                                    if str(id["port_id"]) == remote_iface:
                                        try:
                                            remote_iface = str(id["port_name"])
                                        except Exception as err:
                                            pass
                            remote_sysname = parse1.find('lldp-remote-system-name')
                            if remote_sysname != None:
                                remote_sysname = str(remote_sysname.text)
                            else:
                                try:
                                    parse2 = root1.findall('lldp-neighbor-information')[1]
                                    remote_sysname = parse2.find('lldp-remote-system-name')
                                    if remote_sysname != None:
                                        remote_sysname = str(remote_sysname.text)
                                except Exception as err:
                                    # print(err)
                                    remote_sysname = None
                            if remote_sysname != None:
                                if str(remote_sysname).endswith('.tech.mosreg.ru'):
                                    remote_sysname = remote_sysname.replace('.tech.mosreg.ru', '')
                            if local_iface != None and remote_iface != None and remote_sysname != None and not self.mac_regex.match(remote_iface):
                                my_lldp.append({local_iface: {"remote_iface": remote_iface, "remote_hostname": remote_sysname}})
                    dev.close()
                    sys.stderr = sys.__stderr__
                    lldp_list_correct = self.uniq_list(my_lldp)
                    if lldp_list_correct != []:
                        lldp_dict = {"local_hostname": host_name, "lldp_list": lldp_list_correct, "zbx_data": kwargs}
                        return [True, lldp_dict]
                    else:
                        return [False, None, host_name]
                except Exception as err:
                    print(err)
                    return  [False, None, host_name]

            def start_Junos(self,**kwargs):
                tags = kwargs['tags']
                for tag in tags:
                    if tag['tag'] == "device_role" and tag['value'] == "core":
                        result = self.conn_Juniper_rpc(**kwargs)
                        return result
                    else:
                        result = self.conn_Juniper_cli_via_rpc(**kwargs)
                        return result


