


from remote_system.core.keep_api_connect import netbox_api_instance
from remote_system.core.netbox_get import NetboxGet



class NBSync(NetboxGet):


    def __init__(self):
        super().__init__()
        self.nb = netbox_api_instance.get_instance()


    def sync_devices(self):
        list_devices = self.get_all_devices()
        return list_devices


if __name__ == "__main__":
    call = NBSync()
    result = call.sync_devices()
    for dev in result:
        print(dev)
