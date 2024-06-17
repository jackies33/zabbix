

from pyzabbix import ZabbixAPIException



import logging
import sys

sys.path.append('/opt/zabbix_custom/')

from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.parser_and_preparing import BaseDeviceDataGet





class Creator_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and create the host in zabbix1
    """

    def __init__(self, data=None):
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()
        #self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.DEBUG)
        #file_handler = logging.FileHandler('/opt/zabbix_custom/remote_system/executor_with_hosts/logging.txt')
        #file_handler.setLevel(logging.DEBUG)
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #file_handler.setFormatter(formatter)
        #self.logger.addHandler(file_handler)


    def create_host(self):
        """
        Method for create device(host) in zabbix1
        """
        data = self.get_device_data()
        #self.logger.debug(f"\n\nStarting to create host with data: {data}\n\n")
        try:
            self.zapi.host.create(
                host=data["name"],
                interfaces=[{
                    'type': 2,
                    'main': 1,
                    'useip': 1,
                    'ip': "127.199.199.199",# Temporary ip address until update with correct address
                    'dns': '',
                    'port': "161",
                    'details': {
                            'version': 2,
                            'community': data["snmp_comm"]
                    }
                }],
                proxy_hostid=str(data["proxy_id"]),
                groups=[{'groupid': int(data["group_id"])}],
                templates=[{'templateid': int(data["template_id"])}],
                status=data["host_status"]
            )
            #self.logger.debug(f"\n\nHost creation successful1: {host_id}\n\n")
            host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': data["phys_address"]}})
            self.zapi.host.update(hostid=host_id, tags=[
                                                        {'tag': "device_role", 'value': data['device_role']},
                                                        {'tag': "remote_id", 'value': data['host_id_remote']},
                                            ]
                                  )
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            #self.logger.debug(f"\n\nHost creation successful2: {created_host}\n\n")
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]


    def create_host_full(self):
        """
        Method for create device(host) in zabbix1
        """
        data = self.get_data_for_full_create()
        try:
            self.zapi.host.create(
                host=data["name"],
                interfaces=[{
                    'type': 2,
                    'main': 1,
                    'useip': 1,
                    'ip': data["ip_address"],
                    'dns': '',
                    'port': "161",
                    'details': {
                            'version': 2,
                            'community': data["snmp_comm"]
                    }
                }],
                proxy_hostid=str(data["proxy_id"]),
                groups=[{'groupid': int(data["group_id"])}],
                templates=[{'templateid': int(data["template_id"])}],
                status=data["host_status"]
            )
            host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': data["phys_address"]}})
            self.zapi.host.update({'hostid': host_id,'inventory': {'serialno_a': data['serial']}})
            tags_1 = [{'tag': "device_role", 'value': data['device_role']},{'tag': "remote_id", 'value': data['host_id_remote']}]
            custom_dict = data['custom_fields']
            tags = [{'tag': key, 'value': value['name']} if isinstance(value, dict) and 'name' in value else {'tag': key,'value': str(value)}for key, value in custom_dict.items()]
            full_tags = tags_1 + tags
            self.zapi.host.update(hostid=host_id, tags=full_tags)
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]




#my_wh = {'event': 'created', 'timestamp': '2024-06-13 09:05:45.245413+00:00', 'model': 'device', 'username': 'admin', 'request_id': 'b13b8dd9-9aef-43c3-9a5f-ec07bbc39785', 'data': {'id': 492, 'url': '/api/dcim/devices/492/', 'display': '2k-asw-9-56-1-0.0', 'name': '2k-asw-9-56-1-0.0', 'device_type': {'id': 9, 'url': '/api/dcim/device-types/9/', 'display': 'EX3400-48P', 'manufacturer': {'id': 1, 'url': '/api/dcim/manufacturers/1/', 'display': 'Juniper Networks', 'name': 'Juniper Networks', 'slug': 'juniper-networks'}, 'model': 'EX3400-48P', 'slug': 'Ex3400-48P'}, 'device_role': {'id': 1, 'url': '/api/dcim/device-roles/1/', 'display': 'asw', 'name': 'asw', 'slug': 'asw'}, 'tenant': {'id': 4, 'url': '/api/tenancy/tenants/4/', 'display': 'gku_mo_moc_ikt', 'name': 'gku_mo_moc_ikt', 'slug': 'gku_mo_moc_ikt'}, 'platform': {'id': 3, 'url': '/api/dcim/platforms/3/', 'display': 'Juniper.JUNOS', 'name': 'Juniper.JUNOS', 'slug': 'juniper-junos'}, 'serial': '', 'asset_tag': None, 'site': {'id': 14, 'url': '/api/dcim/sites/14/', 'display': '2k', 'name': '2k', 'slug': '2k'}, 'location': None, 'rack': None, 'position': None, 'face': None, 'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': None, 'primary_ip': None, 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'description': '', 'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh', 'MAP_Group': None, 'Name_of_Establishment': None, 'TG_Group': {'id': 3, 'url': '/api/tenancy/contact-roles/3/', 'display': 'TG_Group_MOCIKT_Main', 'name': 'TG_Group_MOCIKT_Main', 'slug': 'tg_group_mocikt_main'}}, 'created': '2024-06-13T12:05:45.189689+03:00', 'last_updated': '2024-06-13T12:05:45.189706+03:00'}, 'snapshots': {'prechange': None, 'postchange': {'created': '2024-06-13T09:05:45.189Z', 'last_updated': '2024-06-13T09:05:45.189Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 9, 'device_role': 1, 'tenant': 4, 'platform': 3, 'name': '2k-asw-9-56-1-0.0', 'serial': '', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields': {'Connection_Scheme': 'ssh', 'TG_Group': 3}, 'tags': []}}}
#call = Creator_Hosts(my_wh)
#result = call.create_host()
#print(result)