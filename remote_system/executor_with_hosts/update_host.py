



from ..core.mappings import GetMappings
from ..core.parser_and_preparing import BaseDeviceDataGet
from ..core.keep_api_connect import zabbix_api_instance




class Updater_Hosts(BaseDeviceDataGet):
    """
    Legacy class for handling information and update the host in zabbix
    """

    def __init__(self, **kwargs):
        self.result = None
        data = kwargs["data_ext"]
        self.changes = kwargs["changes"]
        super().__init__(data)
        self.zapi = zabbix_api_instance.get_instance()

    def update_host(self):
        """
        Method for update device(host) in zabbix
        """
        try:
            data = self.get_device_data()
            for change in self.changes:
                Mapp = GetMappings()
                for wh_essence, zbx_essense in Mapp.wh_update_mapping_essence.items():
                    if change in wh_essence:
                        for command in zbx_essense:
                            exec(command)

            return [True, self.result]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]


