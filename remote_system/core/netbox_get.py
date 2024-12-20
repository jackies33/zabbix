


from concurrent.futures import ThreadPoolExecutor, as_completed
import re


from remote_system.core.keep_api_connect import netbox_api_instance
from remote_system.core.nb_sync.classifier_for_sync import CLASSIFIER


class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()
        self.pattern_clear_host_name_sw = re.compile(r'\.\d+$')

    def get_nb_data_for_device(self,device_self):
        try:
            device = self.nb.dcim.devices.get(name=device_self)
            if device == None:
                print(device_self)
                vc = self.nb.dcim.virtual_chassis.get(name=device_self)
                print(vc)
                vc_name = vc.master.name
                device = self.nb.dcim.devices.get(name=str(vc_name))
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
            device_role = device.role
            device_type = device.device_type
            classification = CLASSIFIER(device_type, device_role, custom_filed)
            #AuProf = classification.classifier_AuthProf(device_type, device_role)
            #AuthScheme = classification.classifier_AuthScheme(custom_filed)
            site = device.site.id
            site = self.nb.dcim.sites.get(id=site)
            phys_address = str(site.physical_address)
            my_address = None
            if name_of_establishmnet != None:
                my_address = (f'{phys_address}\n({name_of_establishmnet})')
            vc_enable = device.virtual_chassis
            manufacturer = device_type.manufacturer.name
            serial = device.serial
            host_name = device.name
            host_name_for_clear = str(host_name)
            sn = device.serial
            if "kr01-mng" not in host_name_for_clear and "kr02-mng" not in host_name_for_clear:
                cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
            elif host_name_for_clear == "kr02-mng-dsw01.1":
                cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
            else:
                cleaned_hostname = host_name_for_clear
            if str(cleaned_hostname).endswith('.tech.mosreg.ru'):
                cleaned_hostname = cleaned_hostname.replace('.tech.mosreg.ru', '')
            my_address = str(site.physical_address)
            if name_of_establishmnet:
                my_address = f'{my_address}\n({name_of_establishmnet})'
            return {
                'host_name': str(cleaned_hostname), 'host_status': str(device.status), 'site': site,
                'host_id_remote': str(device.id), 'tenant': str(device.tenant), 'manufacturer': str(manufacturer),
                'device_role': str(device_role), 'tg_resource_group': tg_resource_group,
                'platform': str(device.platform), 'map_resource_group': map_resource_group,
                'device_type': str(device_type), 'my_address': my_address, 'ip_address': primary_ip, 'sn': sn,
                'custom_fields': custom_filed,
            }
        except ValueError as e:
            print(f"\n\n{e}\n\nfailed extract ManagedObject!!!\n\n")
            return None
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
                if "wap" in str(host_name) or "AWMP" in str(host_name):
                    return None
                else:
                    primary_ip = device.primary_ip
                    if primary_ip is None:
                        return None
                    host_name_for_clear = str(host_name)
                    if "kr01-mng" not in host_name_for_clear and "kr02-mng" not in host_name_for_clear:
                        cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
                    elif host_name_for_clear == "kr02-mng-dsw01.1":
                        cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
                    else:
                        cleaned_hostname = host_name_for_clear
                    if str(cleaned_hostname).endswith('.tech.mosreg.ru'):
                        cleaned_hostname = cleaned_hostname.replace('.tech.mosreg.ru', '')
                    primary_ip = str(primary_ip).split('/')[0]
                    custom_filed = dict(device.custom_fields)
                    tg_resource_group_dict = device.custom_fields.get("TG_Group")
                    map_resource_group_dict = device.custom_fields.get("MAP_Group")
                    name_of_establishmnet = device.custom_fields.get('Name_of_Establishment')
                    tg_resource_group = tg_resource_group_dict.get("name") if tg_resource_group_dict else None
                    map_resource_group = map_resource_group_dict.get("name") if map_resource_group_dict else None
                    device_role = device.role
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
                        'host_name': str(cleaned_hostname), 'host_status': str(device.status), 'site': site,
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


    def get_device_vc(self, **kwargs):
        try:
            master_id = kwargs['master']['id']
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
            device_role = device.role
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
            host_name_for_clear = str(host_name)
            sn = device.serial
            if "kr01-mng" not in host_name_for_clear and "kr02-mng" not in host_name_for_clear:
                cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
            elif host_name_for_clear == "kr02-mng-dsw01.1":
                cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
            else:
                cleaned_hostname = host_name_for_clear
            if str(cleaned_hostname).endswith('.tech.mosreg.ru'):
                cleaned_hostname = cleaned_hostname.replace('.tech.mosreg.ru', '')
            my_address = str(site.physical_address)
            if name_of_establishmnet:
                my_address = f'{my_address}\n({name_of_establishmnet})'
            return {
                'host_name': str(cleaned_hostname), 'host_status': str(device.status), 'site': site,
                'host_id_remote': str(device.id), 'tenant': str(device.tenant), 'manufacturer': str(manufacturer),
                'device_role': str(device_role), 'tg_resource_group': tg_resource_group,
                'platform': str(device.platform), 'map_resource_group': map_resource_group,
                'device_type': str(device_type), 'my_address': my_address, 'ip_address': primary_ip, 'sn': sn,
                'custom_fields': custom_filed,
            }
        except Exception as err:
           return [False,err]




