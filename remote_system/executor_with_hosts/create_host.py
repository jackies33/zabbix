

from pyzabbix import ZabbixAPIException




import sys

sys.path.append('/opt/zabbix1')

from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.parser_and_preparing import BaseDeviceDataGet


class Creator_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and create the host in zabbix1
    """

    def __init__(self, data):
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

    def create_host(self):
        """
        Method for create device(host) in zabbix1
        """
        data = self.get_device_data()
        #netboxget = NetboxGet()
        #phys_address = netboxget.get_phys_address(**self.data)
        try:
            host_id = self.zapi.host.create(
                host=data["name"],
                interfaces=[{
                    'type': 2,
                    'main': 1,
                    'useip': 1,
                    'ip': "127.199.199.199",# Временный адрес пока ip пустой до update по device с актуальным адресом
                    'dns': '',
                    'port': "161",
                    'details': {
                            'version': 2,
                            'community': data["snmp_comm"]
                    }
                }],
                proxy_hostid=str(data["proxy_id"]),
                groups=[{'groupid': int(data["group_id"])}],
                templates=[{'templateid': int(data["template_id"])}]
            )
            host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': data["phys_address"]}})
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]


    def create_host_full(self):
        """
        Method for create device(host) in zabbix1
        """
        data = self.get_data_for_full_create()
        try:
            host_id = self.zapi.host.create(
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
                templates=[{'templateid': int(data["template_id"])}]
            )
            host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': data["phys_address"]}})
            self.zapi.host.update({'hostid': host_id,'inventory': {'serialno_a': data['serial']}})
            custom_dict = data['custom_fields']
            tags = [{'tag': key, 'value': value['name']} if isinstance(value, dict) and 'name' in value else {'tag': key,'value': str(value)}for key, value in custom_dict.items()]
            self.zapi.host.update(hostid=host_id, tags=tags)
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]



