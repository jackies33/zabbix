



import logging
import re


from externaljober.zabbix.zabbix import ZBX_PROC


class PROCEDURE_AP():

    def __init__(self,**kwargs):
        self.item_count_up = "AP_Count_UP_floor"
        self.item_count_down = "AP_Count_DOWN_floor"
        self.item_all_counting_up = "AP_ALL_Counting_UP"
        self.item_all_counting_down = "AP_ALL_Counting_DOWN"
        self.value_type = 3
        self.item_type = 2
        self.mapings_aps_group = {"wap-dpmo":"DPMO","wap-novator":"2k"}
        self.aw_hostname = kwargs['aw_hostname']
        self.aw_host_id = kwargs['aw_host_id']


    def process_ap(self, ap, interface_id, ap_data_list, wap_dict_from_nb):
        """Process Access Point data and collect data for Zabbix"""
        try:
            #print(wap_dict_from_nb)
            wap_list_from_nb = wap_dict_from_nb['devices_list']
            wap_scope_name = wap_dict_from_nb['wap_scope_hostname']
            facility_name = wap_scope_name.split("wap-")[1]
            ap_name = ap.get('name', None)
            ap_sn = ap.get('serial_number', None)
            if ap_name:
                    host_first_location = None
                    host_second_location = None
                    for nb_wap in wap_list_from_nb:
                        if str(nb_wap['host_sn']) == str(ap_sn):
                            if str(nb_wap['host_status']) == "Active":
                                ap_name = nb_wap.get("host_name",None)
                                ap_sn = str(nb_wap['host_sn'])
                                #print(ap_name)
                                host_third_location = nb_wap.get("host_third_location", None)
                                host_second_location = nb_wap.get('host_second_location',None)
                                host_first_location = nb_wap.get('host_first_location',None)
                                #print(ap_name)
                                ap_id = ap.get('@id', None)
                                ap_status = ap.get('is_up', None)
                                if ap_status == 'true':
                                    ap_status = 'UP'
                                elif ap_status == 'false':
                                    ap_status = 'DOWN'
                                else:
                                    ap_status = 'DOWN'
                                if ap_name and host_first_location and host_second_location:
                                    try:
                                        ap_name = f"{facility_name}_{ap_name}"
                                        ap_data = [
                                            (ap_id, ap_name, ap_status, 'AP_Status', 'status', 4, 2),
                                            #(ap_id, ap_name, ap_sn, 'AP_SN', 'sn', 4, 2),
                                        ]

                                        for data in ap_data:
                                            ap_id, ap_name, ap_value, item_name, key_suffix, value_type, item_type = data
                                            if ap_id and ap_name and ap_value is not None:
                                                key = f"{facility_name}.ap.{ap_id}.{key_suffix}"
                                                tags = []
                                                if host_third_location != None:
                                                    tags = [{'tag': 'data_type', 'value': item_name},
                                                            # {'tag': 'AP_name', 'value': ap_name},
                                                            {'tag': 'floor', 'value': host_first_location},
                                                            {'tag': 'location', 'value': host_second_location},
                                                            {'tag': 'name_of_ap', 'value': host_third_location},
                                                            {'tag': 'serial_number', 'value': ap_sn}]
                                                elif host_third_location == None:
                                                    tags = [{'tag': 'data_type', 'value': item_name},
                                                            # {'tag': 'AP_name', 'value': ap_name},
                                                            {'tag': 'floor', 'value': host_first_location},
                                                            {'tag': 'location', 'value': host_second_location},
                                                            {'tag': 'serial_number', 'value': ap_sn}]
                                                #{'tag': 'AP_ID', 'value': ap_id}]
                                                item_full_name = f"{item_name} -- {ap_name}"
                                                zbx = ZBX_PROC()
                                                for_create_item = {
                                                                   "host_name":self.aw_hostname,
                                                                   "host_id": self.aw_host_id,
                                                                   "item_name": item_full_name,
                                                                   "item_key": key,
                                                                   "tags": tags, "value_type": 4, "item_type": 2,
                                                                   "wap_name": ap_name, "create_trigger": True,
                                                                   "check_sn": True,
                                                                   "host_sn_for_check": ap_sn
                                                                   }
                                                item_id = zbx.create_item(**for_create_item)
                                                # item_id = zbx.create_item(host_id, f"{item_name} -- {ap_name}", key, tags, value_type, item_type)

                                                if item_id:
                                                    if item_id[0] == True:
                                                        ap_data_list.append(f"{self.aw_hostname} {key} {ap_value}")
                                                        return [
                                                                True,
                                                                {"item_id":item_id[1],"item_key":key},
                                                                {"floor": host_first_location, "value": ap_status}
                                                        ]

                                                else:
                                                    return [False, (ap_id,ap_name,ap_value)]
                                            else:
                                                return [False, (ap_id,ap_name,ap_value)]
                                    except Exception as e:
                                        logging.error(f"Error processing AP {ap_name} with ID {ap_id}: {e}")
                                        return [False,e]
                                else:
                                    return [False,(wap_scope_name,host_first_location,host_second_location)]
                            else:
                                return [False,ap_name]
        except Exception as err:
            return [False,err]

    def process_count_ap(self,ap_dict_count,wap_name_scope):
        facility_name = wap_name_scope.split("wap-")[1]
        zbx = ZBX_PROC()
        count_data_list = []
        count_data_list_for_reddis = []
        up_dict = ap_dict_count['count_up']
        down_dict = ap_dict_count['count_down']
        up_counting = 0
        down_counting = 0
        for key, value in up_dict.items():
            try:

                up_counting = up_counting + value
                floor_number = re.findall(r"-?\d+", key)
                if floor_number:
                    floor_number = floor_number[0].strip()
                #print(floor_number)
                #if facility_name == "novator":
                #    floor_number = key.split("Этаж")[0].strip()
                #elif facility_name == "dpmo":
                #    floor_number = key.split("Этаж")[1].strip()
                tags = [{'tag': 'floor', 'value': key},{'tag': 'data_type', 'value': f"Count_UP_{facility_name}"}]# {'tag': 'location', 'value': host_second_location}]
                item_key = f"{facility_name}.ap_count_up.floor.{floor_number}"
                item_id = zbx.create_item(**{"host_id":self.aw_host_id, "item_name": f"{facility_name}-{self.item_count_up}_{key}", "item_key":item_key,
                                                                   "tags":tags, "value_type": self.value_type,
                                             "item_type": self.item_type, "wap_name":None, "create_trigger":False,
                                             "check_sn": False,
                                             "host_sn_for_check":None
                                             })
                #print(f"ITEM ID -   {item_id}")
                if item_id:
                    count_data_list.append(f"{self.aw_hostname} {item_key} {value}")
                    count_data_list_for_reddis.append({"item_id":item_id[1],"item_key":item_key})


            except Exception as err:
                print(err)
        for key2, value2 in down_dict.items():
            try:
                down_counting = down_counting + value2
                floor_number = re.findall(r"-?\d+", key2)
                if floor_number:
                    floor_number = floor_number[0].strip()
                #print(floor_number)
                #if facility_name == "novator":
                #    floor_number = key2.split("Этаж")[0].strip()
                #elif facility_name == "dpmo":
                #    floor_number = key2.split("Этаж")[1].strip()
                tags = [{'tag': 'floor', 'value': key2},{'tag': 'data_type', 'value': f"Count_Down_{facility_name}"}]# {'tag': 'location', 'value': host_second_location}]
                item_key2 = f"{facility_name}.ap_count_down.floor.{floor_number}"
                item_id2 = zbx.create_item(**{"host_id":self.aw_host_id, "item_name": f"{facility_name}-{self.item_count_down}_{key2}", "item_key":item_key2,
                                                                   "tags":tags, "value_type": self.value_type,
                                             "item_type": self.item_type, "wap_name": None, "create_trigger":False,
                                              "check_sn": False,
                                              "host_sn_for_check": None
                                              })
                #print(f"ITEM ID -   {item_id2}")
                if item_id2:
                    count_data_list.append(f"{self.aw_hostname} {item_key2} {value2}")
                    count_data_list_for_reddis.append({"item_id": item_id2[1], "item_key": item_key2})


            except Exception as err:
                print(err)
        item_id_all_up = zbx.create_item(**{"host_id": self.aw_host_id, "item_name": f"{facility_name}-{self.item_all_counting_up}", "item_key": f"{facility_name}.ap_all_count_up",
                           "tags": [{'tag': 'data_type', 'value': f"Count_ALL_UP_{facility_name}"}], "value_type": self.value_type,
                           "item_type": self.item_type, "wap_name": None, "create_trigger": False,
                                            "check_sn": False,
                                            "host_sn_for_check": None
                                            })
        if item_id_all_up:
            count_data_list.append(f"{self.aw_hostname} {facility_name}.ap_all_count_up {up_counting}")
            count_data_list_for_reddis.append({"item_id": item_id_all_up[1], "item_key": f"{facility_name}.ap_all_count_up"})


        item_id_all_down = zbx.create_item(**{"host_id": self.aw_host_id, "item_name": f"{facility_name}-{self.item_all_counting_down}", "item_key": f"{facility_name}.ap_all_count_down",
                           "tags": [{'tag': 'data_type', 'value': f"Count_ALL_DOWN_{facility_name}"}], "value_type": self.value_type,
                           "item_type": self.item_type, "wap_name": None, "create_trigger": False,
                                              "check_sn": False,
                                              "host_sn_for_check": None
                                              })
        if item_id_all_down:
            count_data_list.append(f"{self.aw_hostname} {facility_name}.ap_all_count_down {down_counting}")
            count_data_list_for_reddis.append({"item_id": item_id_all_down[1],"item_key": f"{facility_name}.ap_all_count_down"})


        return [count_data_list,count_data_list_for_reddis]






