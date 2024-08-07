

import sys

sys.path.append('/opt/zabbix_custom/')

from remote_system.core.parser_and_preparing import BaseDeviceDataGet
from remote_system.core.keep_api_connect import zabbix_api_instance




class Remover_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and delete the host in zabbix1
    """

    def __init__(self, data):
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

    def remove_host(self):
        """
        Method for delete device(host) in zabbix1
        """
        try:
            data = self.get_id()
            host_id = data['host_id_local']
            result = self.zapi.host.delete(host_id)
            return [True,result]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]


