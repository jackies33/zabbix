


import sys
import time
from pyzabbix import ZabbixAPIException

#sys.path.append('/opt/zabbix1')
sys.path.append('/opt/zabbix_custom/')

from remote_system.core.mappings import GetMappings
from remote_system.core.parser_and_preparing import BaseDeviceDataGet
from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.zabbix_get import GetHost
from remote_system.core.netbox_get import NetboxGet
from remote_system.executor_with_hosts.create_host import Creator_Hosts



class Updater_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and update the host in zabbix1
    """

    def __init__(self, **kwargs):
        #self.result = None
        data = kwargs["data_ext"]
        self.changes = kwargs["changes"]
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

        #self.host_id = None
        #self.interface_id = None

    def update_host(self,ds):
        """
        Method for update device(host) in zabbix1
        """
        try:
            list_results = []
            if ds == "webhook":
                data = self.get_device_data()# would be use in mappings commands
            elif ds == "export":
                data = self.get_data_for_full_create()
            else:
                data = self.get_device_data()
            mappings = GetMappings()
            for change in self.changes:#create loop where would be try to find essences between webhooks and mappings keys for make some change in zabbix data
                    if change in mappings.wh_update_mapping_essence:
                        method_name = mappings.wh_update_mapping_essence[change]
                        method = getattr(mappings, method_name)
                        try:
                            result = method(data)  # Call the method from GetMappings
                            list_results.append(result)
                        except Exception as e:
                            print(f'Error executing command for {change}: {e}')
                            list_results.append(e)
            return [True, list_results]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]
        #finally:
        #    # Reset all data variables
        #    self.result = None
        ##    self.changes = None
         #   self.host_id = None
         #   self.interface_id = None
         #   data = None

    def update_vc(self):
        """
        Method for update device(host) in zabbix1 by data from vc model
        """
        try:
            data = self.get_vc_data()
            time.sleep(35)
            get_zbx = GetHost()
            hosts_delete = get_zbx.get_vc_hosts(**data)
            if hosts_delete == None:
                return False
            else:
                get_nb = NetboxGet()
                data_nb = get_nb.get_device_vc(**data)
                if data_nb == False:
                    return False
                else:
                    create = Creator_Hosts({"data":data_nb})
                    result = create.create_host_full()
                    return result
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]



     ##       for change in self.changes:
      #          Mapp = GetMappings()
      #          for wh_essence, zbx_essense in Mapp.wh_update_mapping_essence.items():  # create loop where would be try to find essences between webhooks and mappings keys for make some change in zabbix data
      #              if change in wh_essence:
       #                 for command in zbx_essense:
       ##     return [True, self.result]
        #except Exception as e:
        #    print(f'Error: {e}')
        #    return [False, e]
#changes = {'last_updated': {'prechange': '2024-04-08T17:20:14.637Z', 'postchange': '2024-06-14T09:19:30.848Z'}, 'device_type': {'prechange': 9, 'postchange': 2}, 'device_role': {'prechange': 1, 'postchange': 2}, 'name': {'prechange': '2k-asw-2-108-1-0.1', 'postchange': '2k-dopme-asw-2-108-1-0.1'}, 'custom_fields': {'prechange': {'TG_Group': 3, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}, 'postchange': {'TG_Group': 2, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}}}
#data = {'event': 'updated', 'timestamp': '2024-06-14 09:19:30.876439+00:00', 'model': 'device', 'username': 'admin', 'request_id': '94db0b3f-8507-46c3-8a4f-8b7501208d29', 'data': {'id': 206, 'url': '/api/dcim/devices/206/', 'display': '2k-dopme-asw-2-108-1-0.1', 'name': '2k-dopme-asw-2-108-1-0.1', 'device_type': {'id': 2, 'url': '/api/dcim/device-types/2/', 'display': 'EX2200-48P-4G', 'manufacturer': {'id': 1, 'url': '/api/dcim/manufacturers/1/', 'display': 'Juniper Networks', 'name': 'Juniper Networks', 'slug': 'juniper-networks'}, 'model': 'EX2200-48P-4G', 'slug': 'ex2200-48p-4g'}, 'device_role': {'id': 2, 'url': '/api/dcim/device-roles/2/', 'display': 'P/PE', 'name': 'P/PE', 'slug': 'ppe'}, 'tenant': {'id': 4, 'url': '/api/tenancy/tenants/4/', 'display': 'gku_mo_moc_ikt', 'name': 'gku_mo_moc_ikt', 'slug': 'gku_mo_moc_ikt'}, 'platform': {'id': 3, 'url': '/api/dcim/platforms/3/', 'display': 'Juniper.JUNOS', 'name': 'Juniper.JUNOS', 'slug': 'juniper-junos'}, 'serial': 'NY0220100936', 'asset_tag': None, 'site': {'id': 14, 'url': '/api/dcim/sites/14/', 'display': '2k', 'name': '2k', 'slug': '2k'}, 'location': None, 'rack': None, 'position': None, 'face': None, 'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': None, 'primary_ip': {'id': 164, 'url': '/api/ipam/ip-addresses/164/', 'display': '10.100.15.2/24', 'family': 4, 'address': '10.100.15.2/24'}, 'primary_ip4': {'id': 164, 'url': '/api/ipam/ip-addresses/164/', 'display': '10.100.15.2/24', 'family': 4, 'address': '10.100.15.2/24'}, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': {'id': 18, 'url': '/api/dcim/virtual-chassis/18/', 'display': '2k-asw-2-108-1-0', 'name': '2k-asw-2-108-1-0', 'master': {'id': 206, 'url': '/api/dcim/devices/206/', 'display': '2k-asw-2-108-1-0.1', 'name': '2k-asw-2-108-1-0.1'}}, 'vc_position': 1, 'vc_priority': None, 'description': '', 'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh', 'MAP_Group': None, 'Name_of_Establishment': None, 'TG_Group': {'id': 2, 'url': '/api/tenancy/contact-roles/2/', 'display': 'TG_Group_OGV_IKMO_tsp', 'name': 'TG_Group_OGV_IKMO_tsp', 'slug': 'tg_group_ogv_ikmo_tsp'}}, 'created': '2024-04-08T20:20:10.635029+03:00', 'last_updated': '2024-06-14T12:19:30.848647+03:00'}, 'snapshots': {'prechange': {'created': '2024-04-08T17:20:10.635Z', 'last_updated': '2024-04-08T17:20:14.637Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 9, 'device_role': 1, 'tenant': 4, 'platform': 3, 'name': '2k-asw-2-108-1-0.1', 'serial': 'NY0220100936', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': 164, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': 18, 'vc_position': 1, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 3, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}, 'tags': []}, 'postchange': {'created': '2024-04-08T17:20:10.635Z', 'last_updated': '2024-06-14T09:19:30.848Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 2, 'device_role': 2, 'tenant': 4, 'platform': 3, 'name': '2k-dopme-asw-2-108-1-0.1', 'serial': 'NY0220100936', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': 164, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': 18, 'vc_position': 1, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}, 'tags': []}}}
#call = Updater_Hosts(**{"data_ext":data,"changes":changes})
#result = call.update_host('webhook')
#print(result)


