


import os
import sys
#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append("/app/")
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.core.zabbix_get import GetHost
from map_manager.core.netbox_get import GetNBData


class GetData():
    """
    class for get info about host from zabbix and get info from host
    """
    def __init__(self):
        self.ZBX_GET = GetHost()
        self.NB_GET = GetNBData()

    def get_hosts_info_zbx(self,**kwargs):
        target_essence = kwargs["essence"]
        if target_essence == "device_role":
            devices = self.ZBX_GET.get_devices_by_device_role(kwargs["essence_value"])
            return devices
        elif target_essence == "MAP_Group":
            devices = self.ZBX_GET.get_devices_from_map(kwargs["essence_value"])
            return devices

    def get_host_id(self,host_name):
        host_id = self.ZBX_GET.get_local_id(host_name)
        if host_id[0] == True:
            return host_id[1]
        else:
            return None

    def get_all_maps_from_zbx(self):
        all_maps = self.ZBX_GET.get_all_exist_maps()
        return all_maps

    def get_all_maps_groups(self):
        map_groups = self.NB_GET.get_all_MAP_groups()
        return map_groups

    def get_all_hosts_in_zabbix(self,hosts_list):
        all_devices = self.ZBX_GET.get_all_exists_hosts_by_connection_from_devices(hosts_list)
        return all_devices





