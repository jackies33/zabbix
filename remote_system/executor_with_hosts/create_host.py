import time

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
                            'community': data["snmp_comm"],
                            #'bulk': '1', #for enable bulk requests
                    }
                }],
                #proxy_hostid=str(data["proxy_id"]),
                groups=[{'groupid': int(data["group_id"])}],
                templates=[{'templateid': int(data["template_id"])}],
                status=data["host_status"]
            )
            #self.logger.debug(f"\n\nHost creation successful1: {host_id}\n\n")
            time.sleep(2)
            host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
            self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
            self.zapi.host.update({'hostid': host_id,'inventory': {'location': data["phys_address"]}})
            self.zapi.host.update(hostid=host_id, tags=[
                                                        {'tag': "device_role", 'value': data['device_role']},
                                                        {'tag': "remote_id", 'value': data['host_id_remote']},
                                                        {'tag': "tenant", 'value': data['tenant']},
                                    ]
                                  )
            created_host = self.zapi.host.get(filter={"name": data["name"]})
            #self.logger.debug(f"\n\nHost creation successful2: {created_host}\n\n")
            return [True,created_host]
        except ZabbixAPIException as err:
            return [False,err]
        except TypeError as err:
            return [False, err]


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
                            'community': data["snmp_comm"],
                            #'bulk': '0', #for disable bulk requests
                    }
                }],
                #proxy_hostid=str(data["proxy_id"]),
                groups=[{'groupid': int(data["group_id"])}],
                templates=[{'templateid': int(data["template_id"])}],
                status=data["host_status"]
            )
            time.sleep(2)
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
            try:
                self.zapi.host.create(
                    host=data["name"](),
                    interfaces=[{
                        'type': 2,
                        'main': 1,
                        'useip': 1,
                        'ip': data["ip_address"],
                        'dns': '',
                        'port': "161",
                        'details': {
                            'version': 2,
                            'community': data["snmp_comm"],
                            #'bulk': '0', #for disable bulk requests
                        }
                    }],
                    # proxy_hostid=str(data["proxy_id"]),
                    groups=[{'groupid': int(data["group_id"])}],
                    templates=[{'templateid': int(data["template_id"])}],
                    status=data["host_status"]
                )
                time.sleep(2)
                host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']
                self.zapi.host.update({'hostid': host_id, 'inventory_mode': 0})
                self.zapi.host.update({'hostid': host_id, 'inventory': {'location': data["phys_address"]}})
                self.zapi.host.update({'hostid': host_id, 'inventory': {'serialno_a': data['serial']}})
                tags_1 = [{'tag': "device_role", 'value': data['device_role']},
                          {'tag': "remote_id", 'value': data['host_id_remote']},
                          {'tag': "tenant", 'value': data['tenant']},
                          ]
                custom_dict = data['custom_fields']
                tags = [
                    {'tag': key, 'value': value['name']} if isinstance(value, dict) and 'name' in value else {'tag': key,
                                                                                                              'value': str(
                                                                                                                  value)}
                    for key, value in custom_dict.items()]
                full_tags = tags_1 + tags
                self.zapi.host.update(hostid=host_id, tags=full_tags)
                created_host = self.zapi.host.get(filter={"name": data["name"]})
                return [True, created_host]
            except ZabbixAPIException as err:
                return [False,err]
            except TypeError as err:
                return [False, err]



