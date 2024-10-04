



from airwaveapiclient import AirWaveAPIClient, APList
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time

from my_env import AW_API_LOGIN, AW_API_PASSWD, AW_BASE_URL, AW_HOSTNAME
from keep_api_connect import zabbix_api_instance

"""
message_logger1 = logging.getLogger('debug_messages')
message_logger1.setLevel(logging.INFO)
file_handler1 = logging.FileHandler('/var/log/zabbix_custom/zabbix_WRK/AirWaveAP/debug1.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler1.setFormatter(formatter)
message_logger1.addHandler(file_handler1)
"""

class ZBX_PROC():
    def __init__(self):
        self.zapi = zabbix_api_instance.get_instance()
        self.down_status_macros = "{$DOWN_STATUS_WAP}"
        self.up_status_macros = "{$UP_STATUS_WAP}"


    def get_host_interface(self, host_id):
        """Get host's interface"""
        try:
            interfaces = self.zapi.hostinterface.get(filter={"hostid": host_id})
            if interfaces:
                return interfaces[0]['interfaceid']
        except Exception as err:
           #logging.error(f"Error getting host interface: {err}")
            return [False,err]
        return None

    def create_or_get_host(self, hostname):
        """Get host's id"""
        try:
            host = self.zapi.host.get(filter={"host": hostname})
            host_id = host[0]['hostid']
        except Exception as err:
            #logging.error(f"Error getting or creating host: {err}")
            return [False,err]
        return host_id

    def create_trigger(self, **kwargs):
        try:
            time.sleep(1)
            kwargs["tags"].append({"tag": "alarm_name","value":"WAP DOWN"})
            self.zapi.trigger.create(
                description=kwargs["item_name"],
                expression=f"last(/{AW_HOSTNAME}/{kwargs['item_key']})={self.down_status_macros}",
                recovery_mode=1,
                recovery_expression=f"last(/{AW_HOSTNAME}/{kwargs['item_key']})={self.up_status_macros}",
                priority=3,
                comments=kwargs["item_name"],
                event_name=f"{kwargs['wap_name']} is Down",
                tags=kwargs["tags"]
            )
            # trigger_id = trigger_id.get('triggerids', [])[0]
        except Exception as err:
            print(err)
            #message_logger1.error(err)

    def create_item(self, **kwargs):

        """Create item and get its id or just get id in zabbix"""
        try:
            item = self.zapi.item.get(filter={"hostid": kwargs["host_id"], "key_": kwargs["item_key"]})
            if not item:
                item_id = self.zapi.item.create(
                    hostid=kwargs["host_id"],
                    name=kwargs["item_name"],
                    key_=kwargs["item_key"],
                    type=kwargs["item_type"],
                    value_type=kwargs["value_type"],
                    interfaceid=0,
                    tags=kwargs["tags"],
                )['itemids'][0]
                if kwargs["create_trigger"] == True:
                    self.create_trigger(**kwargs)
                return [True,item_id]
            else:
                item_id = item[0]['itemid']
            triggers = None
            if kwargs["create_trigger"] == True:
                try:
                    triggers = self.zapi.trigger.get(filter={"event_name": "{kwargs['wap_name']} is Down"})
                except Exception as err:
                    message_logger1.error(err)
                    return [True, item_id]
                # trigger_id = None
                if triggers:
                    # trigger_id = triggers[0]['triggerid']
                    return [True, item_id]
                elif not triggers:
                    self.create_trigger(**kwargs)
                    return [True,item_id]
            elif kwargs["create_trigger"] == False:
                return [True, item_id]
        except Exception as err:
            message_logger1.error(err)
            return [False,err]




class PROCEDURE_AP():

    def __init__(self):
        self.item_count_up = "AP_Count_UP_floor"
        self.item_count_down = "AP_Count_DOWN_floor"
        self.item_all_counting_up = "AP_ALL_Counting_UP"
        self.item_all_counting_down = "AP_ALL_Counting_DOWN"
        self.value_type = 3
        self.item_type = 2
    def process_ap(self, ap, host_id, interface_id, ap_data_list, wap_list_from_nb):
        """Process Access Point data and collect data for Zabbix"""
        try:

            ap_name = ap.get('name', None)
            ap_sn = ap.get('serial_number', None)
            if ap_name:
                    wap_name = None
                    host_first_location = None
                    host_second_location = None
                    for wap in wap_list_from_nb:
                        if str(wap['host_sn']) == str(ap_sn):
                            wap_name = wap["host_name"]
                            host_second_location = wap['host_second_location']
                            host_first_location = wap['host_first_location']
                            #print(ap_name)
                            ap_id = ap.get('@id', None)
                            ap_client_count = ap.get('client_count', None)
                            #ap_controller_id = ap.get('controller_id', None)
                            #ap_device_category = ap.get('device_category', None)
                            #ap_firmware = ap.get('firmware', None)
                            #ap_lan_ip = ap.get('lan_ip', None)
                            #ap_lan_mac = ap.get('lan_mac', None)
                            #ap_ssid = ap.get('ssid', None)
                            #ap_group = ap.get('group', {}).get('#text', None)
                            ap_status = ap.get('is_up', None)
                            if ap_status == 'true':
                                ap_status = 'UP'
                            elif ap_status == 'false':
                                ap_status = 'DOWN'
                            else:
                                ap_status = 'DOWN'
                            #ap_uptime = ap.get('snmp_uptime', None)
                            #ap_radio = ap.get('radio', [])
                            if wap_name and host_first_location and host_second_location:
                                try:
                                    wap_name = f"{wap_name}({host_first_location}).({host_second_location})"
                                    ap_data = [
                                        #(ap_id, wap_name, ap_client_count, 'AP_Client_Count', 'client_count', 3, 2),
                                        #(ap_id, wap_name, ap_controller_id, 'AP_Controller_ID', 'controller_id', 3, 2),
                                        #(ap_id, ap_name, ap_firmware, 'AP_Firmware', 'firmware', 4, 2),
                                        #(ap_id, ap_name, ap_lan_ip, 'AP_LAN_IP', 'lan_ip', 4, 2),
                                        #(ap_id, wap_name, ap_lan_mac, 'AP_LAN_MAC', 'lan_mac', 4, 2),
                                        #(ap_id, wap_name, ap_ssid, 'AP_SSID', 'ssid', 4, 2),
                                        #(ap_id, ap_name, ap_group, 'AP_Group', 'group', 4, 2),
                                        (ap_id, wap_name, ap_status, 'AP_Status', 'status', 4, 2),
                                        #(ap_id, wap_name, ap_uptime, 'AP_Uptime', 'uptime', 4, 2),
                                        (ap_id, wap_name, ap_sn, 'AP_SN', 'sn', 4, 2),
                                        #(ap_id, wap_name, host_first_location, 'AP_Floor', 'floor', 4, 2),
                                        #(ap_id, wap_name, host_second_location, 'AP_Location', 'location', 4, 2),
                                        #(ap_id, ap_name, ap_radio, 'AP_Radio_scope', 'radio', 4, 2),
                                    ]

                                    for data in ap_data:
                                        ap_id, ap_name, ap_value, item_name, key_suffix, value_type, item_type = data
                                        if ap_id and ap_name and ap_value is not None:
                                            key = f"ap.{ap_id}.{key_suffix}"
                                            #{host_first_location}.{host_second_location}
                                            tags = [{'tag': 'data_type', 'value': item_name},#{'tag': 'AP_name', 'value': ap_name},
                                                    {'tag': 'floor', 'value':host_first_location}, {'tag': 'location', 'value':host_second_location},
                                                    {'tag': 'serial_number', 'value':ap_sn}]
                                            #{'tag': 'AP_ID', 'value': ap_id}]
                                            zbx = ZBX_PROC()
                                            for_create_item = {"host_id":host_id, "item_name": f"{item_name} -- {ap_name}", "item_key":key,
                                                               "tags":tags, "value_type": 4, "item_type": 2, "wap_name":ap_name, "create_trigger":True}
                                            item_id = zbx.create_item(**for_create_item)
                                            #item_id = zbx.create_item(host_id, f"{item_name} -- {ap_name}", key, tags, value_type, item_type)

                                            if item_id:
                                                if item_id[0] == True:
                                                    ap_data_list.append(f"{AW_HOSTNAME} {key} {ap_value}")
                                                    return [True,item_id[1],{"floor":host_first_location,"value":ap_status}]
                                            else:
                                                return item_id
                                        else:
                                            return [False, (ap_id,ap_name,ap_value) ]
                                except Exception as e:
                                    logging.error(f"Error processing AP {ap_name} with ID {ap_id}: {e}")
                                    return [False,e]
                            else:
                                return [False,(wap_name,host_first_location,host_second_location)]
        except Exception as err:
            return [False,err]

    def process_count_ap(self,host_id, ap_dict_count):
        zbx = ZBX_PROC()
        count_data_list = []
        up_dict = ap_dict_count['count_up']
        down_dict = ap_dict_count['count_down']
        up_counting = 0
        down_counting = 0
        for key, value in up_dict.items():
            up_counting = up_counting + value
            floor_number = key.split("Этаж")[1].strip()
            tags = [{'tag': 'floor', 'value': key},{'tag': 'data_type', 'value': "Count_Down"}]# {'tag': 'location', 'value': host_second_location}]
            value_type = 3
            item_type = 2
            item_key = f"ap_count_up.floor.{floor_number}"
            item_id = zbx.create_item(**{"host_id":host_id, "item_name": f"{self.item_count_up}_{key}", "item_key":item_key,
                                                               "tags":tags, "value_type": self.value_type,
                                         "item_type": self.item_type, "wap_name":None, "create_trigger":False})
            if item_id:
                count_data_list.append(f"{AW_HOSTNAME} {item_key} {value}")
        for key2, value2 in down_dict.items():
            down_counting = down_counting + value2
            floor_number = key2.split("Этаж")[1].strip()
            tags = [{'tag': 'floor', 'value': key2},{'tag': 'data_type', 'value': "Count_Down"}]# {'tag': 'location', 'value': host_second_location}]
            value_type = 3
            item_type = 2
            item_key2 = f"ap_count_down.floor.{floor_number}"
            item_id2 = zbx.create_item(**{"host_id":host_id, "item_name": f"{self.item_count_down}_{key2}", "item_key":item_key2,
                                                               "tags":tags, "value_type": self.value_type,
                                         "item_type": self.item_type, "wap_name": None, "create_trigger":False})
            if item_id2:
                count_data_list.append(f"{AW_HOSTNAME} {item_key2} {value2}")
        item_id_all_up = zbx.create_item(**{"host_id": host_id, "item_name": self.item_all_counting_up, "item_key": "ap_all_count_up.dpmo",
                           "tags": [{'tag': 'data_type', 'value': "Count_ALL_UP"}], "value_type": self.value_type,
                           "item_type": self.item_type, "wap_name": None, "create_trigger": False})
        if item_id_all_up:
            count_data_list.append(f"{AW_HOSTNAME} ap_all_count_up.dpmo {up_counting}")
        item_id_all_down = zbx.create_item(**{"host_id": host_id, "item_name": self.item_all_counting_down, "item_key": "ap_all_count_down.dpmo",
                           "tags": [{'tag': 'data_type', 'value': "Count_ALL_DOWN"}], "value_type": self.value_type,
                           "item_type": self.item_type, "wap_name": None, "create_trigger": False})
        if item_id_all_down:
            count_data_list.append(f"{AW_HOSTNAME} ap_all_count_down.dpmo {down_counting}")
        return count_data_list



def start_process(wap_list_from_nb):
    try:
        client = AirWaveAPIClient(url=AW_BASE_URL, username=AW_API_LOGIN, password=AW_API_PASSWD)
        client.login()
        ap_list_response = client.ap_list()
        ap_list_xml = ap_list_response.text
        ap_list = APList(ap_list_xml)
       # for ap in ap_list:
        #    print(ap)
        zbx = ZBX_PROC()
        host_id = zbx.create_or_get_host(AW_HOSTNAME)
        interface_id = zbx.get_host_interface(host_id)
        if not interface_id:
            print("Error: No interface found for the host")
            return
        ap_data_list = []
        ap_count_dict = {"count_up":
            {
                "Этаж -3": 0, "Этаж -2": 0, "Этаж -1": 0, "Этаж 1": 0, "Этаж 2": 0, "Этаж 3": 0, "Этаж 4": 0,
                "Этаж 5": 0, "Этаж 6": 0, "Этаж 7": 0, "Этаж 8": 0, "Этаж 9": 0, "Этаж 10": 0, "Этаж 11": 0,
                "Этаж 12": 0, "Этаж 14": 0, "Этаж 15": 0, "Этаж 16": 0, "Этаж 17": 0
            },
            "count_down":
                {"Этаж -3": 0, "Этаж -2": 0, "Этаж -1": 0, "Этаж 1": 0, "Этаж 2": 0, "Этаж 3": 0, "Этаж 4": 0,
                 "Этаж 5": 0, "Этаж 6": 0, "Этаж 7": 0, "Этаж 8": 0, "Этаж 9": 0, "Этаж 10": 0, "Этаж 11": 0,
                 "Этаж 12": 0, "Этаж 14": 0, "Этаж 15": 0, "Этаж 16": 0, "Этаж 17": 0}
        }
        AP_PROCEDURE = PROCEDURE_AP()
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(AP_PROCEDURE.process_ap, ap, host_id, interface_id, ap_data_list, wap_list_from_nb) for ap in ap_list]
            for future in as_completed(futures):
                result = future.result()  # Ensure any raised exceptions are caught
                if result:
                    if result[0] == True:
                        result_count = result[2]
                        if result_count['value'] == "UP":
                            ap_count_dict['count_up'][result_count['floor']] = ap_count_dict['count_up'][result_count['floor']] + 1
                        elif result_count['value'] == "DOWN":
                            ap_count_dict['count_down'][result_count['floor']] = ap_count_dict['count_down'][result_count['floor']] + 1
            #AP_PROCEDURE = PROCEDURE_AP()
            count_data_list = AP_PROCEDURE.process_count_ap(host_id,ap_count_dict)
                #print(result)
        client.logout()
        return [True,ap_data_list,count_data_list]
    except Exception as err:
        return [False,err]











