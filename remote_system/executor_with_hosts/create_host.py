

from pyzabbix import ZabbixAPIException




import sys

sys.path.append('/opt/zabbix1')

from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.parser_and_preparing import BaseDeviceDataGet
from remote_system.core.netbox_get import NetboxGet




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
        netboxget = NetboxGet()
        phys_address = netboxget.get_phys_address(**self.data)
        try:
            host_id = self.zapi.host.create(
                host=data["name"],
                interfaces=[{
                    'type': 2,
                    'main': 1,
                    'useip': 1,
                    'ip': "129.29.29.29",# Временный адрес пока ip пустой до update по device с актуальным адресом
                    'dns': "",
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
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': phys_address}})
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]



