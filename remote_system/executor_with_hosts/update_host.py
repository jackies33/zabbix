


import sys
import time

sys.path.append('/opt/zabbix1')

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
        self.result = None
        data = kwargs["data_ext"]
        self.changes = kwargs["changes"]
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

    def update_host(self):
        """
        Method for update device(host) in zabbix1
        """
        try:
            data = self.get_device_data()# would be use in mappings commands
            for change in self.changes:
                Mapp = GetMappings()
                for wh_essence, zbx_essense in Mapp.wh_update_mapping_essence.items():# create loop where would be try to find essences between webhooks and mappings keys for make some change in zabbix data
                    if change in wh_essence:
                        for command in zbx_essense:
                            exec(command)

            return [True, self.result]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]

    def update_vc(self):
        """
        Method for update device(host) in zabbix1 by data from vc model
        """
        try:
            data = self.get_vc_data()
            time.sleep(15)
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

