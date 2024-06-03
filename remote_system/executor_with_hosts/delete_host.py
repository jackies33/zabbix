



from ..core.parser_and_preparing import BaseDeviceDataGet
from ..core.keep_api_connect import zabbix_api_instance




class Remover_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and delete the host in zabbix
    """

    def __init__(self, data):
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

    def remove_host(self):
        """
        Method for delete device(host) in zabbix
        """
        try:
            data = self.get_only_name()
            host_id = self.zapi.host.get(filter={"host": data["name"]})[0]["hostid"]
            result = self.zapi.host.delete(host_id)
            return [True,result]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]


