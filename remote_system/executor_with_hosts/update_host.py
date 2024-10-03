


import sys
import time
import logging

#sys.path.append('/opt/zabbix1')
sys.path.append('/opt/zabbix_custom/')

from remote_system.core.mappings import GetMappings
from remote_system.core.parser_and_preparing import BaseDeviceDataGet
from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.zabbix_get import GetHost
from remote_system.core.netbox_get import NetboxGet
from remote_system.executor_with_hosts.create_host import Creator_Hosts



message_logger2 = logging.getLogger('update_flow')
message_logger2.setLevel(logging.INFO)
file_handler = logging.FileHandler('/var/log/zabbix_custom/remote_system/update_host_flow.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
message_logger2.addHandler(file_handler)


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

    def update_vc(self):
        """
        Method for update device(host) in zabbix1 by data from vc model
        """
        try:
            # data = self.get_vc_data()
            time.sleep(40)
            get_zbx = GetHost()
            hosts_delete = get_zbx.get_vc_hosts(**self.data)
            get_nb = NetboxGet()
            data_nb_for_vc = get_nb.get_device_vc(**self.data)
            message_logger2.info(f"DATA for VC UPDATE : {data_nb_for_vc}")
            if data_nb_for_vc == False:
                return False
            else:
                create = Creator_Hosts({"data": data_nb_for_vc})
                result = create.create_host_full()
                message_logger2.info(f"RESULT for VC UPDATE : {data_nb_for_vc}")
                return result
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]

