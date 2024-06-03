

from my_env import my_path_sys
import sys

sys.path.append(my_path_sys)


from remote_system.executor_with_hosts.create_host import Creator_Hosts
from remote_system.executor_with_hosts.delete_host import Remover_Hosts
from remote_system.executor_with_hosts.update_host import Updater_Hosts


from parser_and_preparing import Parser_Json
#from tg_bot import telega_bot





class Handler_WebHook():
    """

    class for proccessing web_hooks from netbox

    """

    def __init__(self):
        """


        """

    def core_handler(self,**kwargs):

        ext_data_type = kwargs["data_type"]
        data_ext = kwargs["data"]
        call = Parser_Json()
        try:
            if ext_data_type == "netbox_main":
                event_classifier = call.event_classifier(**data_ext)
                if event_classifier[0] == True:
                    event = event_classifier[1]['event']
                    if event == "deleted":
                        deleting = Remover_Hosts(data_ext)
                        result = deleting.remove_host()
                        return result
                    elif event == "updated":
                        #parse_data = call.parser_create_and_update(**data_ext)
                        changes = call.compare_changes(**data_ext)
                        updating = Updater_Hosts(**{"changes": changes, "data_ext": data_ext})
                        result = updating.update_host()
                        return changes
                        #return [changes,parse_data,"updated"]
                        #print("update")
                    elif event == "created":
                        #parse_data = call.parser_create_and_update(**data_ext)
                        creating = Creator_Hosts(data_ext)
                        result = creating.create_host()
                        return result
                    elif event == "update_before_delete":
                        return ["skip update because before delete"]
                        #print("skip update because before delete")

                    else:

                        tg_massage = f"it was a problem with web_hook from netbox, " \
                                     f"please check the log in netbox and web_handler for" \
                                     f" get additional information |   ERROR from handler \n>>> {event_classifier[1]} <<<\n"
                        print(tg_massage)
                        return [False,tg_massage]


                elif event_classifier[0] == False:
                         tg_massage = f"it was a problem with web_hook from netbox, " \
                                 f"please check the log in netbox and web_handler for" \
                                 f" get additional information |   ERROR from handler \n>>> {event_classifier[1]} <<<\n"
                         print(tg_massage)
                         return [False, tg_massage]
        except Exception as err:
            return [False, err]




#my_wh = {'event': 'updated', 'timestamp': '2024-05-31 09:11:24.299874+00:00', 'model': 'device', 'username': 'admin', 'request_id': 'c573b91d-fd5f-40e0-b4f2-2b311f716166', 'data': {'id': 230, 'url': '/api/dcim/devices/230/', 'display': 'mfc-035-ar01', 'name': 'mfc-035-ar01', 'device_type': {'id': 8, 'url': '/api/dcim/device-types/8/', 'display': 'AR6120', 'manufacturer': {'id': 2, 'url': '/api/dcim/manufacturers/2/', 'display': 'Huawei Technologies Co.', 'name': 'Huawei Technologies Co.', 'slug': 'huawei-technologies-co'}, 'model': 'AR6120', 'slug': 'ar6120'}, 'device_role': {'id': 2, 'url': '/api/dcim/device-roles/2/', 'display': 'P/PE', 'name': 'P/PE', 'slug': 'ppe'}, 'tenant': {'id': 4, 'url': '/api/tenancy/tenants/4/', 'display': 'gku_mo_moc_ikt', 'name': 'gku_mo_moc_ikt', 'slug': 'gku_mo_moc_ikt'}, 'platform': {'id': 2, 'url': '/api/dcim/platforms/2/', 'display': 'Huawei.VRP', 'name': 'Huawei.VRP', 'slug': 'huawei-vrp'}, 'serial': '6R20A0005415', 'asset_tag': None, 'site': {'id': 14, 'url': '/api/dcim/sites/14/', 'display': '2k', 'name': '2k', 'slug': '2k'}, 'location': None, 'rack': None, 'position': None, 'face': None, 'parent_device': None, 'status': {'value': 'active', 'label': 'Active'}, 'airflow': {'value': 'left-to-right', 'label': 'Left to right'}, 'primary_ip': {'id': 184, 'url': '/api/ipam/ip-addresses/184/', 'display': '10.100.169.35/32', 'family': 4, 'address': '10.100.169.35/32'}, 'primary_ip4': {'id': 184, 'url': '/api/ipam/ip-addresses/184/', 'display': '10.100.169.35/32', 'family': 4, 'address': '10.100.169.35/32'}, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'description': '', 'comments': '', 'config_template': None, 'local_context_data': None, 'tags': [], 'custom_fields': {'Connection_Scheme': 'ssh', 'MAP_Group': None, 'Name_of_Establishment': '', 'TG_Group': {'id': 2, 'url': '/api/tenancy/contact-roles/2/', 'display': 'TG_Group_OGV_IKMO_tsp', 'name': 'TG_Group_OGV_IKMO_tsp', 'slug': 'tg_group_ogv_ikmo_tsp'}}, 'created': '2024-05-31T12:11:20.441135+03:00', 'last_updated': '2024-05-31T12:11:24.277301+03:00'}, 'snapshots': {'prechange': {'created': '2024-05-31T09:11:20.441Z', 'last_updated': '2024-05-31T09:11:24.168Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 8, 'device_role': 2, 'tenant': 4, 'platform': 2, 'name': 'mfc-035-ar01', 'serial': '6R20A0005415', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': 'left-to-right', 'primary_ip4': None, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': ''}, 'tags': []}, 'postchange': {'created': '2024-05-31T09:11:20.441Z', 'last_updated': '2024-05-31T09:11:24.277Z', 'description': '', 'comments': '', 'local_context_data': None, 'device_type': 8, 'device_role': 2, 'tenant': 4, 'platform': 2, 'name': 'mfc-035-ar01', 'serial': '6R20A0005415', 'asset_tag': None, 'site': 14, 'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': 'left-to-right', 'primary_ip4': 184, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields': {'TG_Group': 2, 'Connection_Scheme': 'ssh', 'Name_of_Establishment': ''}, 'tags': []}}}

#if __name__ == "__main__":
##    data_my = {"data_type": "netbox_main", "data": my_wh}
#    call = Handler_WebHook()
#    result = call.core_handler(**data_my)
#    print(result)

