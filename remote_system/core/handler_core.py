

from my_env import my_path_sys
import sys
#import threading
import datetime

sys.path.append(my_path_sys)


from remote_system.executor_with_hosts.create_host import Creator_Hosts
from remote_system.executor_with_hosts.delete_host import Remover_Hosts
from remote_system.executor_with_hosts.update_host import Updater_Hosts


from remote_system.core.parser_and_preparing import Parser_Json
from remote_system.core.tg_bot import tg_bot





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
        print(data_ext)
        call = Parser_Json()
        try:
            if ext_data_type == "netbox_main":
                event_classifier = call.event_classifier(**data_ext)
                host_name = data_ext['data']['name']
                if event_classifier[0] == True:
                    if event_classifier[1]["target"] == "device":
                        event = event_classifier[1]['event']
                        if event == "deleted":
                            deleting = Remover_Hosts(data_ext)
                            result = deleting.remove_host()
                            #primary_ip = data_ext['primary_ip4']['address']
                            if result[0] == True:
                                tg_message = (
                                    f'ZABBIX.handler[ "Event_Delete Device" ]\n Device Name - '
                                    f'[ "{host_name}" ] \n Time: [ "{datetime.datetime.now()}" ]'
                                )
                                sender = tg_bot(tg_message)
                                sender.tg_sender()
                            return result
                        elif event == "updated":
                            #parse_data = call.parser_create_and_update(**data_ext)
                            changes = call.compare_changes(**data_ext)
                            updating = Updater_Hosts(**{"changes": changes, "data_ext": data_ext})
                            result = updating.update_host("webhook")
                            if result[0] == True:
                                tg_message = (
                                    f'ZABBIX.handler[ "Event_Update Device" ]\n Device Name - '
                                    f'[ "{host_name}" ] \n Time: [ "{datetime.datetime.now()}" ]'
                                )
                                #sender = tg_bot(tg_message)
                                #sender.tg_sender()
                            return result
                            #return [changes,parse_data,"updated"]
                            #print("update")
                        elif event == "created":
                            #parse_data = call.parser_create_and_update(**data_ext)
                            creating = Creator_Hosts(data_ext)
                            result = creating.create_host()
                            if result[0] == True:
                                tg_message = (
                                    f'ZABBIX.handler[ "Event_Create Device" ]\n Device Name - '
                                    f'[ "{host_name}" ] \n Time: [ "{datetime.datetime.now()}" ]'
                                )
                                #sender = tg_bot(tg_message)
                                #sender.tg_sender()
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
                    #elif event_classifier[1]["target"] == "virtualchassis":
                    #    event = event_classifier[1]['event']
                    #    if event == "updated":
                    #        changes = call.compare_changes(**data_ext)
                    #        #result = updating.update_vc()
                    #        thread = threading.Thread(target=lambda: updating.update_vc())# create separated flow for delete device created from webhook and create only one - master
                    #        thread.start()
                elif event_classifier[0] == False:
                         tg_massage = f"it was a problem with web_hook from netbox, " \
                                 f"please check the log in netbox and web_handler for" \
                                 f" get additional information |   ERROR from handler \n>>> {event_classifier[1]} <<<\n"
                         print(tg_massage)
                         return [False, tg_massage]
        except Exception as err:
            return [False, err]



