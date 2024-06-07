


from my_env import my_path_sys
import sys

sys.path.append(my_path_sys)


from remote_system.executor_with_hosts.classifier_for_device import CLASSIFIER
from remote_system.core.zabbix_get import GetProxy,GetGroup,GetTemplate
from remote_system.core.netbox_get import NetboxGet

null = None

class Parser_Json():


    def __init__(self):
        """
        """


    def compare_changes(self ,**data)  :# compare changes between before update and after for add some new value to host
        prechange = data['snapshots']['prechange']
        postchange = data['snapshots']['postchange']
        changes = {}
        for key in postchange:
            if key in prechange:
                if prechange[key] != postchange[key]:
                    changes[key] = {
                        'prechange': prechange[key],
                        'postchange': postchange[key]
                    }
            else:
                changes[key] = {
                    'prechange': None,
                    'postchange': postchange[key]
                }
        return changes

    def event_classifier(self, **file_json):  # find out wich event came for handling
        try:
            null = None
            event = file_json['event']
            target = file_json['model']
            data = file_json['data']
            host_name = data['name']
            if event == "updated":
                find_delete = self.find_out_deleted_updates(**file_json)
                if find_delete == True:
                    event = "update_before_delete"
            result = {
                'host_name': host_name, 'event': event,
                'target': target,
            }
            return [True, result]
        except Exception as e:
            print(f"Error in parser web_hook - {e}")
            return [False, e]

    def find_out_deleted_updates(self,**data):  # before delete event would recieve an update mesagge , and it could be revealed and skip
        snapshots_prechange = data['snapshots']['prechange']
        snapshots_postchange = data['snapshots']['postchange']
        if snapshots_prechange == None:
            if snapshots_postchange != None:
                return True

            else:
                return False
        else:
            return False




class BaseDeviceDataGet:
    """
    Base class for get data from WH.
    """

    def __init__(self, data_ext):
        self.data_ext = data_ext
        self.data = self.data_ext.get("data", {})

    def safe_get(self, dictionary, *keys):

        for key in keys:
            if isinstance(dictionary, dict):
                dictionary = dictionary.get(key)
            else:
                return None
        return dictionary

    def get_only_name(self):
        """
        Method to get only name of the device ecpessially for delete event.
        """
        return {'name':(self.safe_get(self.data, 'name'))}

    def get_device_data(self):
        """
        Method for get information about device from WH
        """
        name = self.safe_get(self.data, 'name')
        device_type = self.safe_get(self.data, 'device_type', 'model')
        manufacturer = self.safe_get(self.data, 'device_type', 'manufacturer', 'name')
        platform = self.safe_get(self.data, 'platform', 'name')
        device_role = self.safe_get(self.data, 'device_role', 'name')
        ip_address = (self.safe_get(self.data, 'primary_ip4', 'address'))
        if ip_address:
            ip_address = ip_address.split("/")[0]
        custom_fields = self.safe_get(self.data, 'custom_fields')
        serial = self.safe_get(self.data, 'serial')
        netboxget = NetboxGet()
        phys_address = netboxget.get_phys_address(**self.data)
        #vc = netboxget.get_vc(**self.data)
        vc = None
        vc = (self.safe_get(self.data,'virtual_chassis', 'master' , 'name'))
        group = f"{manufacturer}/{platform}/{device_type}"
        group_name = GetGroup(group)
        group_id = group_name.get_group()
        templating = GetTemplate(group)
        template_id = templating.classifier_template()
        proxy = GetProxy()
        proxy_id = proxy.get_proxy_next_choise()
        call = CLASSIFIER()
        snmp_comm = call.classifier_snmp_comm \
            (**{"device_type": device_type, "device_role": device_role, "custom_filed": custom_fields})

        device_data = {
            "name": name,
            "device_type": device_type,
            "manufacturer": manufacturer,
            "platform": platform,
            "device_role": device_role,
            "custom_fields": custom_fields,
            "serial": serial,
            "ip_address": ip_address,
            "group": group,
            "group_id": group_id,
            "template_id": template_id,
            "proxy_id": proxy_id,
            "snmp_comm": snmp_comm,
            "phys_address":phys_address,
            "vc":vc,
        }
        return device_data

    def get_data_for_full_create(self):
        """
        Method for preapre information about device from Netbox for full create
        """
        name = self.safe_get(self.data, 'host_name')
        device_type = self.safe_get(self.data, 'device_type')
        manufacturer = self.safe_get(self.data, 'manufacturer')
        platform = self.safe_get(self.data, 'platform')
        device_role = self.safe_get(self.data, 'device_role')
        ip_address = self.safe_get(self.data, 'ip_address')
        if ip_address:
            ip_address = ip_address.split("/")[0]
        custom_fields = self.safe_get(self.data, 'custom_fields')
        tg_group = self.safe_get(self.data, 'tg_resource_group')
        map_group = self.safe_get(self.data, 'map_resource_group')
        name_of_est = self.safe_get(self.data, 'name_of_est')
        serial = self.safe_get(self.data, 'serial')
        phys_address = self.safe_get(self.data, 'phys_address')
        # vc = netboxget.get_vc(**self.data)
        vc = None
        vc = (self.safe_get(self.data, 'virtual_chassis', 'master', 'name'))
        group = f"{manufacturer}/{platform}/{device_type}"
        group_name = GetGroup(group)
        group_id = group_name.get_group()
        templating = GetTemplate(group)
        template_id = templating.classifier_template()
        proxy = GetProxy()
        proxy_id = proxy.get_proxy_next_choise()
        call = CLASSIFIER()
        snmp_comm = call.classifier_snmp_comm \
            (**{"device_type": device_type, "device_role": device_role, "custom_filed": custom_fields})

        device_data = {
            "name": name,
            "device_type": device_type,
            "manufacturer": manufacturer,
            "platform": platform,
            "device_role": device_role,
            "custom_fields": custom_fields,
            "serial": serial,
            "ip_address": ip_address,
            "group": group,
            "group_id": group_id,
            "template_id": template_id,
            "proxy_id": proxy_id,
            "snmp_comm": snmp_comm,
            "phys_address": phys_address,
            "vc": vc,
        }
        return device_data

    def get_vc_data(self):
        """
        Method for get information about devuce from WH
        """
        name = self.safe_get(self.data, 'name')
        master_name = None
        master_id = None
        master_name = self.safe_get(self.data, 'master', 'name')
        master_id = self.safe_get(self.data, 'master', 'id')
        vc_data = {
            "name": name,
            "master_name": master_name,
            "master_id": master_id,
        }
        return vc_data

#wh = {'event': 'updated', 'timestamp': '2024-06-04 09:42:38.740976+00:00', 'model': 'device', 'username': 'admin', 'request_id': '355f9f6c-b91e-4408-8404-735b4e796878', 'data': {'id': 239, 'url': '/api/dcim/devices/239/', 'display': '2k-asw-9-56-1-0.0', 'name': '2k-asw-9-56-1-0.0', 'device_type': {'id': 9, 'url': '/api/dcim/device-types/9/', 'display': 'EX3400-48P', 'manufacturer': {'id': 1, 'url': '/api/dcim/manufacturers/1/', 'display': 'Juniper Networks', 'name': 'Juniper Networks', 'slug': 'juniper-networks'}, 'model': 'EX3400-48P', 'slug': 'Ex3400-48P'}, 'device_role': {'id': 1, 'url': '/api/dcim/device-roles/1/', 'display': 'asw', 'name': 'asw', 'slug': 'asw'}, 'tenant': {'id': 4, 'url': '/api/tenancy/tenants/4/', 'display': 'gku_mo_moc_ikt', 'name': 'gku_mo_moc_ikt', 'slug': 'gku_mo_moc_ikt'}, 'platform': {'id': 3, 'url': '/api/dcim/platforms/3/', 'display': 'Juniper.JUNOS', 'name': 'Juniper.JUNOS', 'slug': 'juniper-junos'}, 'serial': '', 'asset_tag': None, 'site': {'id': 14, 'url': '/api/dcim/sites/14/', 'display': '2k', 'name': '2k', 'slug': '2k'}, 'location': None, 'rack': None, 'position': None, 'face': None, 'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': None, 'primary_ip': None, 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': {'id': 22, 'url': '/api/dcim/virtual-chassis/22/', 'display': '2k-asw-9-56-1-0', 'name': '2k-asw-9-56-1-0', 'master': None}, 'vc_position': 0, 'vc_priority': None, 'description': '', 'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh', 'MAP_Group': None, 'Name_of_Establishment': None, 'TG_Group': {'id': 2, 'url': '/api/tenancy/contact-roles/2/', 'display': 'TG_Group_OGV_IKMO_tsp', 'name': 'TG_Group_OGV_IKMO_tsp', 'slug': 'tg_group_ogv_ikmo_tsp'}}, 'created': '2024-06-04T12:42:37.431751+03:00', 'last_updated': '2024-06-04T12:42:38.716942+03:00'}, 'snapshots': {'prechange': {'created': '2024-06-04T09:42:37.431Z', 'last_updated': '2024-06-04T09:42:37.431Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 9, 'device_role': 1, 'tenant': 4, 'platform': 3, 'name': '2k-asw-9-56-1-0.0', 'serial': '', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'Connection_Scheme': 'ssh'}, 'tags': []}, 'postchange': {'created': '2024-06-04T09:42:37.431Z', 'last_updated': '2024-06-04T09:42:38.716Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 9, 'device_role': 1, 'tenant': 4, 'platform': 3, 'name': '2k-asw-9-56-1-0.0', 'serial': '', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': 22, 'vc_position': 0, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'Connection_Scheme': 'ssh'}, 'tags': []}}}

#call = Parser_Json()
#result = call.compare_changes(**wh)
#print(result)


