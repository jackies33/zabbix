

from keep_api_connect import netbox_api_instance

class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()


    def get_wap_devices(self,**kwargs):
        devices_list = []
        wap_scope_hostname = kwargs['wap_scope_hostname']
        devices = self.nb.dcim.devices.all()
        for dev in devices:
            if wap_scope_hostname in str(dev):
                host_name = dev.name
                host_sn = dev.serial
                host_second_location = dev.location
                location_second = self.nb.dcim.locations.get(id=int(dev.location.id))
                host_first_location = self.nb.dcim.locations.get(id=int(location_second.parent.id))
                devices_list.append({"host_name":str(host_name), "host_sn":str(host_sn), "host_second_location": str(host_second_location),
                                     "host_first_location": str(host_first_location),
                                     })
        return devices_list

