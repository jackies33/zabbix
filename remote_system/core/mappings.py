



import time

from pyzabbix import ZabbixAPIException
import threading

from remote_system.core.keep_api_connect import zabbix_api_instance





class GetMappings():

    def __init__(self):
        self.zapi = zabbix_api_instance.get_instance()

    wh_update_mapping_essence = {
        'primary_ip4': 'primary_ip4',
        'serial': 'serial',
        'custom_fields': 'custom_fields',
        'site': 'site',
        'virtual_chassis': 'virtual_chassis',
        'my_address': "my_address",
        'device_role': "device_role",
        'name': 'name',
        'device_type': 'device_type',
        'status': 'status',
        'tenant': 'tenant',
    }

    """
    group_template_mapping = {
        'Huawei Technologies Co./Huawei.VRP': 'Huawei VRP by SNMP',
        'Juniper Networks/Juniper.JUNOS': 'Juniper Main',
        'MikroTik/MikroTik.RouterOS': 'Mikrotik by SNMP',
        'Hewlett Packard Enterprise/Aruba.ArubaOS': 'Linux by SNMP',
        'Hewlett Packard Enterprise/Aruba.ArubaOS/AP 345': 'Aruba AP',
        'T8/Atlas.OS/': "Atlas.OS",
        'Cisco Systems/Cisco.ASA': "Cisco ASAv by SNMP",
        'Cisco Systems/Cisco.IOS': "Cisco IOS by SNMP",
        'Cisco Systems/Cisco.IOSXR': "Cisco IOSXR by SNMP",
        'Cisco Systems/Cisco.NXOS': "Cisco NXOS by SNMP",
        'Fortinet/Fortinet': "FortiGate by SNMP",
        "Hewlett Packard Enterprise/HP.ProCurve9xxx": "HP Enterprise Switch by SNMP",
        "LENOVO/IBM.NOS": "IBM by SNMP",
        "OS.Linux": "Linux by SNMP",
        "Qtech/Qtech.QSW": "QTech QSW by SNMP",
    }
    """

    group_template_mapping = {
        'Huawei Technologies Co./Huawei.VRP': 'Huawei VRP',
        'Juniper Networks/Juniper.JUNOS': 'Juniper',
        'MikroTik/MikroTik.RouterOS': 'Mikrotik',
        'Hewlett Packard Enterprise/Aruba.ArubaOS': 'ArubaOS',
        'Hewlett Packard Enterprise/Aruba.ArubaOS/AP 345': 'Aruba AP',
        'T8/Atlas.OS/': "Atlas.OS",
        'Cisco Systems/Cisco.ASA': "Cisco ASAv",
        'Cisco Systems/Cisco.IOS': "Cisco IOS",
        'Cisco Systems/Cisco.IOSXE': "Cisco IOSXE",
        'Cisco Systems/Cisco.IOSXR': "Cisco IOSXR",
        'Cisco Systems/Cisco.NXOS': "Cisco NXOS",
        'Fortinet/Fortinet': "FortiGate",
        "Hewlett Packard Enterprise/HP.ProCurve9xxx": "HP Enterprise Switch",
        "LENOVO/IBM.NOS": "IBM",
        "OS.Linux": "Linux",
        "Qtech/Qtech.QSW": "QTech QSW",
    }


    def name(self,data):
        try:
            host_id = data['host_id_local']
            result = self.zapi.host.update(hostid=host_id, host=data['name'])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def status(self,data):
        try:
            host_id = data['host_id_local']
            result = self.zapi.host.update(hostid=host_id, status=data['host_status'])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err
    def primary_ip4(self,data):
        try:
            host_id = data['host_id_local']
            interfaces = self.zapi.hostinterface.get(filter={'hostid': host_id})
            if not interfaces:
                return False
            interface_id = interfaces[0]['interfaceid']
            result = self.zapi.hostinterface.update(interfaceid=interface_id, ip=data['ip_address'])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err


    def serial(self,data):
        try:
            host_id = data['host_id_local']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            serials = self.zapi.host.update({'hostid': host_id, 'inventory': {'serialno_a': data['serial']}})
            host_info = self.zapi.host.get(hostids=host_id, selectInventory=True)
            result = host_info[0].get('inventory', {}).get('serialno_a')
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err


    def custom_fields(self,data):
        try:
            host_id = data['host_id_local']
            custom_dict = data['custom_fields']
            new_tags = [{'tag': key, 'value': value['name']} if isinstance(value, dict) and 'name' in value
                    else {'tag': key, 'value': str(value)} for key, value in custom_dict.items()]
            host = self.zapi.host.get(hostids=host_id, selectTags="extend")[0]
            current_tags = host.get('tags', [])
            for tag in current_tags:
                tag.pop('automatic', None)
                for new_tag in new_tags:
                    if tag['tag'] == new_tag['tag']:
                        tag['value'] = new_tag['value']
                        new_tags.remove(new_tag)
            updated_tags = current_tags + new_tags
            self.zapi.host.update(hostid=host_id, tags=updated_tags)
            host_info = self.zapi.host.get(filter={'hostid': data['host_id_local']}, selectTags='extend')
            name_of_establishment_exists = 'Name_of_Establishment' in custom_dict
            if name_of_establishment_exists:
                self.zapi.host.update({'hostid': host_id, 'inventory': {'location': data['phys_address']}})
            result = host_info[0].get('tags', [])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err


    def device_role(self,data):
        try:
            host_id = data['host_id_local']
            host = self.zapi.host.get(hostids=host_id, selectTags="extend")[0]
            current_tags = host.get('tags', [])
            tag_exists = False
            for tag in current_tags:
                tag.pop('automatic', None)
                if tag['tag'] == 'device_role':
                    tag['value'] = data['device_role']
                    tag_exists = True
            if not tag_exists:
                current_tags.append({'tag': 'device_role', 'value': data['device_role']})
            self.zapi.host.update(hostid=host_id, tags=current_tags, templates= [{'templateid': data['template_id']}])
            host_info = self.zapi.host.get(hostids=host_id, selectTags='extend')
            result = host_info[0].get('tags', [])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def tenant(self,data):
        try:
            host_id = data['host_id_local']
            host = self.zapi.host.get(hostids=host_id, selectTags="extend")[0]
            current_tags = host.get('tags', [])
            tag_exists = False
            for tag in current_tags:
                tag.pop('automatic', None)
                if tag['tag'] == 'tenant':
                    tag['value'] = data['tenant']
                    tag_exists = True
            if not tag_exists:
                current_tags.append({'tag': 'tenant', 'value': data['tenant']})
            self.zapi.host.update(hostid=host_id, tags=current_tags)
            host_info = self.zapi.host.get(hostids=host_id, selectTags='extend')
            result = host_info[0].get('tags', [])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def device_type(self,data):
        try:
            host_id = data['host_id_local']
            result = self.zapi.host.update(hostid=host_id, groups=[{'groupid': data['group_id']}])
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def site(self,data):
        try:
            host_id = data['host_id_local']
            serials = self.zapi.host.update({'hostid': host_id, 'inventory': {'location': data['phys_address']}})
            host_info = self.zapi.host.get(hostids=host_id, selectInventory=True)
            result = host_info[0].get('inventory', {}).get('location')
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def my_address(self,data):
        try:
            host_id = data['host_id_local']
            serials = self.zapi.host.update({'hostid': host_id, 'inventory': {'location': data['phys_address']}})
            host_info = self.zapi.host.get(hostids=host_id, selectInventory=True)
            result = host_info[0].get('inventory', {}).get('location')
            return result
        except ZabbixAPIException as err:
            return err
        except Exception as err:
            return err

    def virtual_chassis(self, data):
        def task():
            try:
                time.sleep(1)
                master_vc_name = data['vc']
                # hosts = self.zapi.host.get(search={'host': master_vc_name}, searchWildcardsEnabled=True, output=['host'])
                # hostnames = [host['host'] for host in hosts]
                # return host_id
                host_id = data['host_id_local']
                host_name = self.zapi.host.get(hostids=host_id, output=['host'])[0]['host']
                #return host_name, host_id, master_vc_name
                if str(host_name) == str(master_vc_name):
                            return False
                elif str(host_name) != str(master_vc_name):
                    result = self.zapi.host.delete(host_id)
                    return result
            except Exception as err:
                return err

        try:
            threading.Thread(target=task).start()
            return "OK"
        except Exception as err:
            return err


