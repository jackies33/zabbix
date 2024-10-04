


from my_env import my_path_sys
import sys
import re

sys.path.append(my_path_sys)


from remote_system.executor_with_hosts.classifier_for_device import CLASSIFIER
from remote_system.core.zabbix_get import GetProxy,GetGroup,GetTemplate,GetHost
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
            if "wap" in str(host_name):
                return [False, "Miss devices, because without monitoring aim"]
            if event == "updated":
                find_delete = self.find_out_deleted_updates(**file_json)
                if find_delete == True:
                    event = "update_before_delete"
            elif "wifi_ap" in host_name:
                event = "missed_device"
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

    def compare_exporter(self,**data):# check differences between remote and local extracted data
        devices_remote = data["devices_remote"]
        devices_local = data["devices_local"]
        exclude_keys = ['manufacturer']
        delete_list = []
        update_list = []
        create_list = []
        differences = {}
        try:
            for dict_remote in devices_remote:
                found = False
                for dict_local in devices_local:
                    if dict_remote.get('host_name') == dict_local.get('host_name'):
                        if dict_remote.get('host_id_remote') == dict_local.get('host_id_remote'):
                            diff = {}
                            for key in dict_remote.keys():
                                local_value = dict_local.get(key)
                                remote_value = dict_remote.get(key)
                                if remote_value == "None":
                                    remote_value = None
                                if local_value == "None":
                                    local_value = None
                                if key not in exclude_keys and local_value != remote_value:
                                    diff.update({key:{'remote_value': remote_value,
                                        'local_value': local_value}})
                            if diff:
                                diff = {"data_ext":{"data":dict_remote},"changes":diff}
                                update_list.append(diff)
                            found = True

                if not found:
                    diff = {"data":dict_remote} #"diff": [{"device_not_exist":"Not Found"}]}
                    create_list.append(diff)
        except TypeError as err:
            print(err)
        try:
            for dict_local in devices_local:
                found = False
                if dict_local.get('host_id_remote') is not None:
                    for dict_remote in devices_remote:
                        if dict_remote.get('host_id_remote') == dict_local.get('host_id_remote'):
                            found = True
                    if not found:
                        diff = {"data":{"name": dict_local['host_name']}}
                                #"diff": [{"for_delete": "Found in local but not in remote"}]}
                        delete_list.append(diff)
        except TypeError as err:
            print(err)
        differences.update({"update":update_list,"create":create_list,"delete":delete_list})
        return differences


class BaseDeviceDataGet:
    """
    Base class for get data from WH.
    """

    def __init__(self, data_ext):
        self.data_ext = data_ext
        self.data = self.data_ext.get("data", {})
        self.pattern_clear_host_name_sw = re.compile(r'\.\d+$')

    def safe_get(self, dictionary, *keys):

        for key in keys:
            if isinstance(dictionary, dict):
                dictionary = dictionary.get(key)
            else:
                return None
        return dictionary

    def get_id(self):
        """
        Method to get only name of the device ecpessially for delete event.
        """
        localid = GetHost()
        host_id_remote = self.safe_get(self.data, 'id')
        name = self.safe_get(self.data, 'name')
        host_id_local = localid.get_local_id(**{"host_name": name, "host_id_remote": str(host_id_remote)})
        return {'name':name,"host_id_local":host_id_local}

    def get_device_data(self):
        """
        Method for get information about device from WH
        """
        name = self.safe_get(self.data, 'name')
        host_id_remote = self.safe_get(self.data, 'id')
        device_type = self.safe_get(self.data, 'device_type', 'model')
        manufacturer = self.safe_get(self.data, 'device_type', 'manufacturer', 'name')
        platform = self.safe_get(self.data, 'platform', 'name')
        device_role = self.safe_get(self.data, 'device_role', 'name')
        ip_address = (self.safe_get(self.data, 'primary_ip4', 'address'))
        host_status = self.safe_get(self.data, 'status', 'label')
        tenant = self.safe_get(self.data, 'tenant')
        if isinstance(tenant, dict):
            tenant = tenant['name']
        if host_status == "Active":
            host_status = "0"
        elif host_status == "Offline":
            host_status = "1"
        else:
            host_status = "0"
        if ip_address:
            ip_address = ip_address.split("/")[0]

        host_name_for_clear = str(name)
        if "kr01-mng" not in host_name_for_clear and "kr02-mng" not in host_name_for_clear:
            cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
        else:
            cleaned_hostname = host_name_for_clear
        if str(cleaned_hostname).endswith('.tech.mosreg.ru'):
            cleaned_hostname = cleaned_hostname.replace('.tech.mosreg.ru', '')

        custom_fields = self.safe_get(self.data, 'custom_fields')
        serial = self.safe_get(self.data, 'serial')
        netboxget = NetboxGet()
        phys_address = None
        phys_address = netboxget.get_phys_address(**self.data)
        try:
            if phys_address[0] == True:
                phys_address = phys_address[1]
        except Exception:
            pass
        netboxget = NetboxGet()
        vc = netboxget.get_vc_master(**self.data)
        try:
            if vc[0] == True:
                vc = vc[1]
            elif vc[0] == False:
                vc = None
        except Exception:
            pass
        #vc = netboxget.get_vc(**self.data)
        #vc = None
        #vc = (self.safe_get(self.data,'virtual_chassis', 'master' , 'name'))
        group = f"{manufacturer}/{platform}/{device_type}"
        group_name = GetGroup(group)
        group_id = group_name.get_group()
        localid = GetHost()
        host_id_local = localid.get_local_id(**{"host_name":name,"host_id_remote":str(host_id_remote)})
        templating = GetTemplate(group,device_role)
        template_id = templating.classifier_template()
        #proxy = GetProxy()
        #proxy_id = proxy.get_proxy_next_choise()
        call = CLASSIFIER()
        snmp_comm = call.classifier_snmp_comm \
            (**{"device_type": device_type, "device_role": device_role, "custom_filed": custom_fields})

        device_data = {
            "name": cleaned_hostname,
            "device_type": device_type,
            "host_id_remote": str(host_id_remote),
            "host_id_local": str(host_id_local),
            "manufacturer": manufacturer,
            "platform": platform,
            "device_role": device_role,
            "custom_fields": custom_fields,
            "serial": serial,
            "ip_address": ip_address,
            "group": group,
            "group_id": group_id,
            "template_id": template_id,
            #"proxy_id": proxy_id,
            "snmp_comm": snmp_comm,
            "phys_address": phys_address,
            "tenant": tenant,
            "vc": vc,
            "host_status": host_status
        }
        return device_data

    def get_data_for_full_create(self):
        """
        Method for preapre information about device from Netbox for full create
        """
        print(self.data)
        name = self.safe_get(self.data, 'host_name')
        device_type = self.safe_get(self.data, 'device_type')
        manufacturer = self.safe_get(self.data, 'manufacturer')
        platform = self.safe_get(self.data, 'platform')
        device_role = self.safe_get(self.data, 'device_role')
        ip_address = self.safe_get(self.data, 'ip_address')
        host_id_remote = self.safe_get(self.data, 'host_id_remote')
        host_status = self.safe_get(self.data, 'host_status')
        tenant = self.safe_get(self.data, 'tenant')
        if isinstance(tenant, dict):
            tenant = tenant['name']

        if host_status == "Active":
            host_status = "0"
        elif host_status == "Offline":
            host_status = "1"
        else:
            host_status = "0"
        if ip_address:
            ip_address = ip_address.split("/")[0]

        host_name_for_clear = str(name)
        if "kr01-mng" not in host_name_for_clear and "kr02-mng" not in host_name_for_clear:
           cleaned_hostname = self.pattern_clear_host_name_sw.sub('', host_name_for_clear)
        else:
            cleaned_hostname = host_name_for_clear
        if str(cleaned_hostname).endswith('.tech.mosreg.ru'):
            cleaned_hostname = cleaned_hostname.replace('.tech.mosreg.ru', '')

        custom_fields = self.safe_get(self.data, 'custom_fields')
        tg_group = self.safe_get(self.data, 'tg_resource_group')
        map_group = self.safe_get(self.data, 'map_resource_group')
        serial = self.safe_get(self.data, 'sn')
        phys_address = None
        phys_address = self.safe_get(self.data, 'my_address')
        # vc = netboxget.get_vc(**self.data)
        netboxget = NetboxGet()
        vc = netboxget.get_vc_master(**self.data)
        try:
            if vc[0] == True:
                vc = vc[1]
            elif vc[0] == False:
                vc = None
        except Exception:
            pass
        group = f"{manufacturer}/{platform}/{device_type}"
        group_name = GetGroup(group)
        group_id = group_name.get_group()
        localid = GetHost()
        host_id_local = localid.get_local_id(**{"host_name": name, "host_id_remote": str(host_id_remote)})
        templating = GetTemplate(group,device_role)
        template_id = templating.classifier_template()
        proxy = GetProxy()
        proxy_id = proxy.get_proxy_next_choise()
        call = CLASSIFIER()
        snmp_comm = call.classifier_snmp_comm \
            (**{"device_type": device_type, "device_role": device_role, "custom_filed": custom_fields})

        device_data = {
            "name": cleaned_hostname,
            "device_type": device_type,
            "host_id_remote":  str(host_id_remote),
            "host_id_local": str(host_id_local),
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
            "tenant": tenant,
            "vc": vc,
            "host_status": host_status,
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




#call  = Parser_Json()
#wh = {'event': 'updated', 'timestamp': '2024-06-14 09:19:30.876439+00:00', 'model': 'device', 'username': 'admin', 'request_id': '94db0b3f-8507-46c3-8a4f-8b7501208d29', 'data': {'id': 206, 'url': '/api/dcim/devices/206/', 'display': '2k-dopme-asw-2-108-1-0.1', 'name': '2k-dopme-asw-2-108-1-0.1', 'device_type': {'id': 2, 'url': '/api/dcim/device-types/2/', 'display': 'EX2200-48P-4G', 'manufacturer': {'id': 1, 'url': '/api/dcim/manufacturers/1/', 'display': 'Juniper Networks', 'name': 'Juniper Networks', 'slug': 'juniper-networks'}, 'model': 'EX2200-48P-4G', 'slug': 'ex2200-48p-4g'}, 'device_role': {'id': 2, 'url': '/api/dcim/device-roles/2/', 'display': 'P/PE', 'name': 'P/PE', 'slug': 'ppe'}, 'tenant': {'id': 4, 'url': '/api/tenancy/tenants/4/', 'display': 'gku_mo_moc_ikt', 'name': 'gku_mo_moc_ikt', 'slug': 'gku_mo_moc_ikt'}, 'platform': {'id': 3, 'url': '/api/dcim/platforms/3/', 'display': 'Juniper.JUNOS', 'name': 'Juniper.JUNOS', 'slug': 'juniper-junos'}, 'serial': 'NY0220100936', 'asset_tag': None, 'site': {'id': 14, 'url': '/api/dcim/sites/14/', 'display': '2k', 'name': '2k', 'slug': '2k'}, 'location': None, 'rack': None, 'position': None, 'face': None, 'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': None, 'primary_ip': {'id': 164, 'url': '/api/ipam/ip-addresses/164/', 'display': '10.100.15.2/24', 'family': 4, 'address': '10.100.15.2/24'}, 'primary_ip4': {'id': 164, 'url': '/api/ipam/ip-addresses/164/', 'display': '10.100.15.2/24', 'family': 4, 'address': '10.100.15.2/24'}, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': {'id': 18, 'url': '/api/dcim/virtual-chassis/18/', 'display': '2k-asw-2-108-1-0', 'name': '2k-asw-2-108-1-0', 'master': {'id': 206, 'url': '/api/dcim/devices/206/', 'display': '2k-asw-2-108-1-0.1', 'name': '2k-asw-2-108-1-0.1'}}, 'vc_position': 1, 'vc_priority': None, 'description': '', 'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh', 'MAP_Group': None, 'Name_of_Establishment': None, 'TG_Group': {'id': 2, 'url': '/api/tenancy/contact-roles/2/', 'display': 'TG_Group_OGV_IKMO_tsp', 'name': 'TG_Group_OGV_IKMO_tsp', 'slug': 'tg_group_ogv_ikmo_tsp'}}, 'created': '2024-04-08T20:20:10.635029+03:00', 'last_updated': '2024-06-14T12:19:30.848647+03:00'}, 'snapshots': {'prechange': {'created': '2024-04-08T17:20:10.635Z', 'last_updated': '2024-04-08T17:20:14.637Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 9, 'device_role': 1, 'tenant': 4, 'platform': 3, 'name': '2k-asw-2-108-1-0.1', 'serial': 'NY0220100936', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': 164, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': 18, 'vc_position': 1, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 3, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}, 'tags': []}, 'postchange': {'created': '2024-04-08T17:20:10.635Z', 'last_updated': '2024-06-14T09:19:30.848Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 2, 'device_role': 2, 'tenant': 4, 'platform': 3, 'name': '2k-dopme-asw-2-108-1-0.1', 'serial': 'NY0220100936', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': 164, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': 18, 'vc_position': 1, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'MAP_Group': None, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': None}, 'tags': []}}}
#result = call.compare_changes(**wh)
#print(result)


