
from ..executor_with_hosts.classifier_for_device import CLASSIFIER
from zabbix_get import GetProxy ,GetGroup ,GetTemplate

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

    def find_out_deleted_updates(self
                                 ,**data):  # before delete event would recieve an update mesagge , and it could be revealed and skip
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
        return self.safe_get(self.data, 'name')

    def get_device_data(self):
        """
        Method for get information about devuce from WH
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
        }
        return device_data
