


from concurrent.futures import ThreadPoolExecutor, as_completed


from remote_system.core.keep_api_connect import netbox_api_instance
from remote_system.core.nb_sync.classifier_for_sync import CLASSIFIER


class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()
    def get_vc_master(self,**kwargs):

        try:
            vc_id = kwargs['virtual_chassis']["id"]
            vc = self.nb.dcim.virtual_chassis.get(id=int(vc_id))
            vc_name = vc.master.name
            return [True,vc_name]
        except Exception as err:
            return [False,err]
    def get_phys_address(self,**kwargs):
        try:
            site_id = kwargs['site']['id']
            site = self.nb.dcim.sites.get(id=site_id)
            my_address = str(site.physical_address)
            device = self.nb.dcim.devices.get(id=kwargs['id'])
            name_of_establishmnet = device.custom_fields['Name_of_Establishment']
            if name_of_establishmnet != None:
                my_address = (f'{my_address}\n({name_of_establishmnet})')
            return [True,my_address]
        except Exception as err:
            return [False,err]

    def get_all_devices(self):
        list_devices = []
        devices = self.nb.dcim.devices.all()

        def process_device(device):
            try:
                host_name = device.name
                if "wap" in str(host_name):
                    return None
                else:
                    primary_ip = device.primary_ip
                    if primary_ip is None:
                        return None
                    primary_ip = str(primary_ip).split('/')[0]
                    custom_filed = dict(device.custom_fields)
                    tg_resource_group_dict = device.custom_fields.get("TG_Group")
                    map_resource_group_dict = device.custom_fields.get("MAP_Group")
                    name_of_establishmnet = device.custom_fields.get('Name_of_Establishment')
                    tg_resource_group = tg_resource_group_dict.get("name") if tg_resource_group_dict else None
                    map_resource_group = map_resource_group_dict.get("name") if map_resource_group_dict else None
                    device_role = device.device_role
                    device_type = device.device_type
                    manufacturer = device_type.manufacturer.name
                    classification = CLASSIFIER(device_type, device_role, custom_filed)
                    site = device.site.id
                    site = self.nb.dcim.sites.get(id=site)
                    my_address = str(site.physical_address)
                    if name_of_establishmnet:
                        my_address = f'{my_address}\n({name_of_establishmnet})'
                    vc_enable = device.virtual_chassis
                    sn = device.serial
                    return {
                        'host_name': str(host_name), 'host_status': str(device.status), 'site': site,
                        'host_id_remote': str(device.id), 'tenant': str(device.tenant), 'manufacturer': str(manufacturer),
                        'device_role': str(device_role), 'tg_resource_group': tg_resource_group,
                        'platform': str(device.platform), 'map_resource_group': map_resource_group,
                        'device_type': str(device_type), 'my_address': my_address, 'ip_address': primary_ip, 'sn': sn,
                        'custom_fields': custom_filed,
                    }
            except ValueError as e:
                print(f"\n\n{e}\n\nfailed extract ManagedObject!!!\n\n")
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(process_device, device) for device in devices]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    list_devices.append(result)

        return list_devices


"""

    def get_all_devices(self):
            list_devices = []
            for device in self.nb.dcim.devices.all():
                try:
                    if device == None:
                        continue
                    primary_ip = device.primary_ip
                    if primary_ip == None:
                        continue
                    primary_ip = str(primary_ip).split('/')[0]
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
                    manufacturer = device_type.manufacturer.name
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
                    sn = device.serial

                    list_devices.append({
                        'host_name': str(host_name), 'host_status': str(device.status), 'site': site,
                        'host_id_remote': str(device.id), 'tenant': str(device.tenant),'manufacturer':str(manufacturer),
                        'device_role': str(device_role), 'tg_resource_group': tg_resource_group,
                        'platform': str(device.platform), 'map_resource_group': map_resource_group,
                        'device_type': str(device_type), 'my_address': my_address, 'ip_address': primary_ip,'sn':sn,
                        'custom_fields':custom_filed,
                    })
                except ValueError as e:
                    print(f"\n\n{e}\n\nfailed extract ManagedObject!!!\n\n")
                    continue
            return list_devices
"""

"""     
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
                'host_id_remote': str(device.id), 'tenant': str(device.tenant),
                'device_role': str(device_role), 'tg_resource_group': str(tg_resource_group),
                'platform': str(device.platform), 'map_resource_group': str(map_resource_group),
                'device_type': str(device_type), 'phys_address': str(phys_address), 'ip_address': str(primary_ip),
                'manufacturer': str(manufacturer), "serial":str(serial), "name_of_est": str(name_of_establishmnet),
                "custom_fields": custom_filed,

            }
            return device_data
        except Exception as err:
           return [False,err]
"""

