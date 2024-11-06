

import re


from externaljober.worker_aruba.mappings import ap_flours_count_list



class PROCEDURE_AP():

    def __init__(self ,**kwargs):
        self.item_count_up = "AP_Count_UP_floor"
        self.item_count_down = "AP_Count_DOWN_floor"
        self.item_all_counting_up = "AP_ALL_Counting_UP"
        self.item_all_counting_down = "AP_ALL_Counting_DOWN"
        self.value_type = 3
        self.item_type = 2
        self.mapings_aps_group = {"wap-dpmo" :"DPMO" ,"wap-novator" :"2k"}
        self.aw_hostname = kwargs['aw_hostname']
        self.aw_host_id = kwargs['aw_host_id']
    def process_ap(self, ap_list, wap_dict_from_nb ,redis_db_items):
        """Process Access Point data and collect data for Zabbix"""
        wap_list_from_nb = wap_dict_from_nb['devices_list']
        wap_scope_name = wap_dict_from_nb['wap_scope_hostname']
        facility_name = wap_scope_name.split("wap-")[1]
        ap_data_list = []
        #ap_count_dict = None
        #for ap_co in ap_flours_count_list:
        #    if ap_co["wap_scope_name"] == wap_scope_name:
        #        ap_count_dict = ap_co['count_dict']
        ap_count_dict = {"count_up": {}, "count_down": {}}
        if ap_count_dict:
            for ap in ap_list:
                try:
                    # message_logger1.info("HERE!")
                    ap_name = ap.get('name', None)
                    # message_logger1.info(ap_name)
                    ap_sn = ap.get('serial_number', None)
                    if ap_name:
                        host_first_location = None
                        host_second_location = None
                        for nb_wap in wap_list_from_nb:
                            if str(nb_wap['host_sn']) == str(ap_sn):
                                if str(nb_wap['host_status']) == "Active":
                                    ap_name = nb_wap.get("host_name" ,None)
                                    ap_sn = str(nb_wap['host_sn'])
                                    #print(ap_name)
                                    host_third_location = nb_wap.get("host_third_location", None)
                                    host_second_location = nb_wap.get('host_second_location' ,None)
                                    host_first_location = nb_wap.get('host_first_location' ,None)
                                    # print(ap_name)
                                    ap_id = ap.get('@id', None)
                                    ap_status = ap.get('is_up', None)
                                    if ap_status == 'true':
                                        ap_status = 'UP'
                                    elif ap_status == 'false':
                                        ap_status = 'DOWN'
                                    else:
                                        ap_status = 'UP'
                                    if ap_name and host_first_location and host_second_location:
                                        try:
                                            ap_name = f"{facility_name}_{ap_name}({host_first_location}).({host_second_location})"
                                            ap_data = [
                                                (ap_id, ap_name, ap_status, 'AP_Status', 'status', 4, 2),
                                                (ap_id, ap_name, ap_sn, 'AP_SN', 'sn', 4, 2),
                                            ]

                                            for data in ap_data:
                                                ap_id, ap_name, ap_value, item_name, key_suffix, value_type, item_type = data
                                                if ap_id and ap_name and ap_value is not None:
                                                    key = f"{facility_name}.ap.{ap_id}.{key_suffix}"
                                                    for redis_item in redis_db_items['data']:
                                                        if redis_item['item_key'] == key:
                                                            item_id = redis_item['item_id']
                                                            if item_id:
                                                                ap_data_list.append(f"{self.aw_hostname} {key} {ap_value}")
                                                                if ap_value == "UP":
                                                                    if host_first_location in ap_count_dict['count_up']:
                                                                        ap_count_dict['count_up'][host_first_location] += 1
                                                                    else:
                                                                        ap_count_dict['count_up'][host_first_location] = 1
                                                                elif ap_value == "DOWN":
                                                                    if host_first_location in ap_count_dict['count_down']:
                                                                        ap_count_dict['count_down'][host_first_location] += 1
                                                                    else:
                                                                        ap_count_dict['count_down'][host_first_location] = 1
                                                                #if ap_value == "UP":
                                                                #    ap_count_dict['count_up'][host_first_location] += 1
                                                                #elif ap_value == "DOWN":
                                                                #    ap_count_dict['count_down'][host_first_location] += 1
                                        except Exception as err:
                                            print(err)

                except Exception as err:
                    return [False ,err]
                    # Собираем все этажи из обоих словарей
        all_floors = set(ap_count_dict["count_up"].keys()).union(ap_count_dict["count_down"].keys())
        # Проверяем каждый этаж и добавляем отсутствующие с результатом 0
        for floor in all_floors:
            if floor not in ap_count_dict["count_up"]:
                ap_count_dict["count_up"][floor] = 0
            if floor not in ap_count_dict["count_down"]:
                ap_count_dict["count_down"][floor] = 0
        return [ap_data_list,ap_count_dict]


    def process_count_ap(self ,ap_dict_count ,wap_name_scope, redis_db_items):
        facility_name = wap_name_scope.split("wap-")[1]
        count_data_list = []
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
                item_key = f"{facility_name}.ap_count_up.floor.{floor_number}"
                for redis_item in redis_db_items['data']:
                    if redis_item['item_key'] == item_key:
                        item_id = redis_item['item_id']
                        if item_id:
                            count_data_list.append(f"{self.aw_hostname} {item_key} {value}")


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
                item_key2 = f"{facility_name}.ap_count_down.floor.{floor_number}"
                for redis_item in redis_db_items['data']:
                    if redis_item['item_key'] == item_key2:
                        item_id2 = redis_item['item_id']
                        if item_id2:
                            count_data_list.append(f"{self.aw_hostname} {item_key2} {value2}")
            except Exception as err:
                print(err)


        for redis_item in redis_db_items['data']:
            if redis_item['item_key'] == f"{facility_name}.ap_all_count_up":
                item_id_all_up = redis_item['item_id']
                if item_id_all_up:
                    count_data_list.append(f"{self.aw_hostname} {facility_name}.ap_all_count_up {up_counting}")

        for redis_item in redis_db_items['data']:
            if redis_item['item_key'] == f"{facility_name}.ap_all_count_down":
                item_id_all_down = redis_item['item_id']
                if item_id_all_down:
                    count_data_list.append(f"{self.aw_hostname} {facility_name}.ap_all_count_down {down_counting}")


        return count_data_list








