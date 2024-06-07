



from remote_system.core.keep_api_connect import netbox_api_instance
from remote_system.core.nb_sync.classifier_for_sync import CLASSIFIER


class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()


    def get_phys_address(self,**kwargs):
        try:
            site_id = kwargs['site']['id']
            site = self.nb.dcim.sites.get(id=site_id)
            my_address = str(site.physical_address)
            return my_address
        except Exception as err:
            return [False,err]



    def get_all_devices(self):
            list_devices = []
            for device in self.nb.dcim.devices.all():
                try:
                    if device == None:
                        continue
                    primary_ip = device.primary_ip
                    if primary_ip == None:
                        continue
                    custom_filed = dict(device.custom_fields)
                    tg_resource_group_dict = device.custom_fields["TG_Group"]
                    map_resource_group_dict = device.custom_fields["MAP_Group"]
                    name_of_establishmnet = device.custom_fields['Name_of_Establishment']
                    tg_resource_group = None
                    map_resource_group = None
                    if tg_resource_group_dict != None:
                        tg_resource_group = tg_resource_group_dict["name"]
                    if map_resource_group_dict != None:
                        map_resource_group = map_resource_group_dict["name"]
                    device_role = device.device_role
                    device_type = device.device_type
                    classification = CLASSIFIER(device_type, device_role, custom_filed)
                    #AuProf = classification.classifier_AuthProf(device_type, device_role)
                    #AuthScheme = classification.classifier_AuthScheme(custom_filed)
                    site = device.site.id
                    site = self.nb.dcim.sites.get(id=site)
                    my_address = str(site.physical_address)
                    if name_of_establishmnet != None:
                        my_address = (f'{my_address}\n({name_of_establishmnet})')
                    vc_enable = device.virtual_chassis
                    host_name = device.name

                    list_devices.append({
                        'host_name': str(host_name), 'host_status': str(device.status), 'site': site,
                        'host_id': int(device.id), 'tenant': str(device.tenant),
                        'device_role': str(device_role), 'tg_resource_group': tg_resource_group,
                        'platform': str(device.platform), 'map_resource_group': map_resource_group,
                        'device_type': str(device_type), 'my_address': my_address, 'ip_address': str(device.primary_ip)
                    })
                except ValueError as e:
                    print(f"\n\n{e}\n\nfailed extract ManagedObject!!!\n\n")
                    continue
            return list_devices
    def get_device_vc(self, **kwargs):
        try:
            master_id = kwargs['master_id']
            device = self.nb.dcim.devices.get(id=master_id)
            if device == None:
                return False
            primary_ip = device.primary_ip.address
            if primary_ip == None:
                return False
            custom_filed = dict(device.custom_fields)
            tg_resource_group_dict = device.custom_fields["TG_Group"]
            map_resource_group_dict = device.custom_fields["MAP_Group"]
            name_of_establishmnet = device.custom_fields['Name_of_Establishment']
            tg_resource_group = None
            map_resource_group = None
            if tg_resource_group_dict != None:
                tg_resource_group = tg_resource_group_dict["name"]
            if map_resource_group_dict != None:
                map_resource_group = map_resource_group_dict["name"]
            device_role = device.device_role
            device_type = device.device_type
            classification = CLASSIFIER(device_type, device_role, custom_filed)
            #AuProf = classification.classifier_AuthProf(device_type, device_role)
            #AuthScheme = classification.classifier_AuthScheme(custom_filed)
            site = device.site.id
            site = self.nb.dcim.sites.get(id=site)
            phys_address = str(site.physical_address)
            if name_of_establishmnet != None:
                my_address = (f'{phys_address}\n({name_of_establishmnet})')
            vc_enable = device.virtual_chassis
            manufacturer = device_type.manufacturer.name
            serial = device.serial
            host_name = device.name
            device_data = {
                'host_name': str(host_name), 'host_status': str(device.status), 'site': site,
                'host_id': int(device.id), 'tenant': str(device.tenant),
                'device_role': str(device_role), 'tg_resource_group': str(tg_resource_group),
                'platform': str(device.platform), 'map_resource_group': str(map_resource_group),
                'device_type': str(device_type), 'phys_address': str(phys_address), 'ip_address': str(primary_ip),
                'manufacturer': str(manufacturer), "serial":str(serial), "name_of_est": str(name_of_establishmnet),
                "custom_fileds": custom_filed,

            }
            return device_data
        except Exception as err:
            return [False,err]


