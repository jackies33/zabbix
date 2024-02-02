


import datetime


#from ..executor_with_hosts.create_host import CreateHost
#from ..executor_with_hosts.delete_host import DeleteHost
#from ..executor_with_hosts.update_host import UpdateHost
from classifier_for_device import CLASSIFIER
#from tg_bot import telega_bot





class Handler_WebHook():
    """

    class for proccessing web_hooks from netbox

    """

    def __init__(self, json_dump):
        self.json_dump = json_dump

    def core_handler(self,*args):
        event_classifier = self.event_classifier(self.json_dump)
        if event_classifier[0] == True:
            event = event_classifier[1]['event']
            if event == "deleted":
                # deleting = DeleteHost(parser_result[1])
                print("delete")
            else:
                parser_result = self.parser_create_update(self.json_dump)# call func , where we will be pars recieved data from netbox's web_hook
                if parser_result[0] == True:
                    result_action_selection = self.action_selection(parser_result[1])
                    #print(parser_result)
                    if result_action_selection[0] == "create":
                        print("create")
                        #creating = CreateHost(parser_result[1])
                    elif result_action_selection[0] == "update":
                        print(f"update for {result_action_selection[1]}")
                        #updating = UpdateHost(parser_result[1])
                    elif result_action_selection[0] == "create_NotReady":
                        print("create_NotReady")
                    elif result_action_selection[0] == "miss_update":
                        print("miss_update")

                elif parser_result[0] == False:
                    tg_massage = f"it was a problem with web_hook from netbox, " \
                                 f"please check the log in netbox and web_handler for" \
                                 f" get additional information | ERROR from handler \n>>> {parser_result[1]} <<<\n"
                    print(tg_massage)

        elif event_classifier[0] == False:
                 tg_massage = f"it was a problem with web_hook from netbox, " \
                         f"please check the log in netbox and web_handler for" \
                         f" get additional information |   ERROR from handler \n>>> {event_classifier[1]} <<<\n"
                 print(tg_massage)
    def event_classifier(self,file_json):
        try:
            null = None
            event = file_json['event']
            target = file_json['model']
            data = file_json['data']
            host_name = data['name']
            result = {
                'host_name': host_name, 'event': event,
                'target': target,
            }
            return [True, result]
        except Exception as e:
            print(f"Error in parser web_hook - {e}")
            return [False, e]



       # elif result[0] == False:
       #     "telegram"


    def parser_create_update(self,file_json):
            try:
                null = None
                event = file_json['event']
                target = file_json['model']
                data = file_json['data']
                # print(data)
                snapshots_prechange = file_json['snapshots']['prechange']
                snapshots_postchange = file_json['snapshots']['postchange']
                host_id = data['id']
                host_name = data['name']
                host_ip_address = data['primary_ip']
                try:
                    host_ip_address = data['primary_ip']['address']
                except Exception as e:
                    print("ip_address is None")
                    host_ip_address = None
                datetime_created = snapshots_postchange['created']
                datetime_updated = snapshots_postchange['last_updated']
                host_status = data['status']['value']
                tenant = data['tenant']['name']
                device_role = data['device_role']['name']
                platform = data['platform']['name']
                device_type = data['device_type']
                manufacturer = device_type['manufacturer']['name']
                device_type = data['device_type']['model']
                custom_field = data['custom_fields']
                classification = CLASSIFIER(device_type, device_role, custom_field)
                snmp_comm = classification.classifier_AuthProf()
                id_site = data['site']['id']
                result = {
                    'host_id': host_id, 'host_ip_address': host_ip_address, 'host_name': host_name,
                    'host_status': host_status, 'tenant': tenant, 'device_role': device_role,
                    'platform': platform, 'manufacturer': manufacturer, 'device_type': device_type,
                    'snmp_comm': snmp_comm, 'conn_scheme': custom_field["Connection_Scheme"],
                    'site': id_site, 'snapshot_prechange': snapshots_prechange, 'event': event,
                    'target': target, 'snapshot_postchange': snapshots_postchange, 'datetime_created':
                        datetime_created, 'datetime_updated': datetime_updated,
                }

                return [True,result]
            except Exception as e:
                print(f"Error in parser web_hook - {e}")
                return [False,e]



    def action_selection(self,wh_dict):
        try:
                null = None
                datetime_created = wh_dict['datetime_created'].split('.')[0]
                datetime_updated = wh_dict['datetime_updated'].split('.')[0]
                datetime_created = datetime.datetime.strptime(datetime_created, "%Y-%m-%dT%H:%M:%S")
                datetime_updated = datetime.datetime.strptime(datetime_updated, "%Y-%m-%dT%H:%M:%S")
                dt_count = datetime_created + datetime.timedelta(seconds=30)
                event = wh_dict['event']
                target = wh_dict['target']
                host_ip_address = wh_dict['host_ip_address']
                if event == "updated" and target == 'device' and host_ip_address != None:
                    if datetime_updated > dt_count:
                        dict1 = wh_dict['snapshot_prechange']
                        dict2 = wh_dict['snapshot_postchange']
                        diff = {k: v for (k, v) in dict1.items() if dict1[k] != dict2[k]}
                        try:
                            snapshot_dif_dict = {'list_for_update': [key for key in diff.keys() if key != 'last_updated']}
                        except AttributeError:
                            print("its not update, its preparing before delete")
                            return ["miss_update",None]
                        return ["update",snapshot_dif_dict]
                    elif datetime_updated < dt_count:
                        return ["create",None]
                elif event == "created" and target == 'device':
                       return ["create_NotReady",None]
        except Exception as e:
            return ['miss_update',None]









"""

### Example of web_hook from netbox 

{'id': 1972, 'url': '/api/dcim/devices/1972/', 'display': '2k-asw-1-1.26.1-0-0', 'name': '2k-asw-1-1.26.1-0-0', 'device_type': 
{'id': 83, 'url': '/api/dcim/device-types/83/', 'display': 'EX3400-24P', 'manufacturer': 
{'id': 19, 'url': '/api/dcim/manufacturers/19/', 'display': 'Juniper Networks', 
'name': 'Juniper Networks', 'slug': 'juniper-networks'}, 'model': 'EX3400-24P', 'slug': 
'Ex3400-24P'}, 'device_role': {'id': 38, 'url': '/api/dcim/device-roles/38/', 
'display': 'c-asw', 'name': 'c-asw', 'slug': 'c-asw'}, 'tenant': 
{'id': 19, 'url': '/api/tenancy/tenants/19/', 'display': 'ЕИМТС', 'name': 'ЕИМТС', 'slug': 'eimts'}, 'platform': 
{'id': 4, 'url': '/api/dcim/platforms/4/', 'display': 'Juniper.JUNOS', 'name': 'Juniper.JUNOS', 'slug': 'juniper-junos'}, 
'serial': 'NW0220090756', 'asset_tag': None, 'site': {'id': 164, 'url': '/api/dcim/sites/164/', 'display': 'Новатор-Кампус',
'name': 'Новатор-Кампус', 'slug': 'novator-campus'}, 'location': {'id': 615, 'url': '/api/dcim/locations/615/', 
'display': '1.26.1', 'name': '1.26.1', 'slug': '1-26-1', '_depth': 1}, 'rack': None, 'position': None, 'face': None,
'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': None, 'primary_ip': 
{'id': 1273, 'url': '/api/ipam/ip-addresses/1273/', 'display': '10.100.15.98/24', 'family': 4, 'address': '10.100.15.98/24'}, 
'primary_ip4': {'id': 1273, 'url': '/api/ipam/ip-addresses/1273/', 
'display': '10.100.15.98/24', 'family': 4, 'address': '10.100.15.98/24'}, 
'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'description': '',
'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh'},
'created': '2024-01-24T11:15:10.825224+03:00', 'last_updated': '2024-01-31T11:35:04.230780+03:00'}

### Example of web_hook from netbox

"""