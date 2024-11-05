



from airwaveapiclient import AirWaveAPIClient, APList
from concurrent.futures import ThreadPoolExecutor, as_completed

from externaljober.my_env import AW_API_LOGIN, AW_API_PASSWD
#from externaljober.worker_aruba.mappings import ap_flours_count_list
from externaljober.zabbix.zabbix import ZBX_PROC
from externaljober.worker_aruba.proccess_wrk_full import PROCEDURE_AP



def start_full_process(wap_dict_from_nb,AW_HOSTNAME):
    try:
        wap_scope_name = wap_dict_from_nb['wap_scope_hostname']
        #ap_count_dict = None
        #for ap_co in ap_flours_count_list:
        #    if ap_co["wap_scope_name"] == wap_scope_name:
        #        ap_count_dict = ap_co['count_dict']
        ap_count_dict = {"count_up": {}, "count_down": {}}
        if ap_count_dict:
            zbx = ZBX_PROC()
            host = zbx.create_or_get_host(AW_HOSTNAME)
            host_id = host['hostid']
            host_name = host['name']
            AW_BASE_URL = host['interfaces'][0]['ip']
            interface_id = zbx.get_host_interface(host_id)
            client = AirWaveAPIClient(url=f"https://{AW_BASE_URL}", username=AW_API_LOGIN, password=AW_API_PASSWD)
            client.login()
            ap_list_response = client.ap_list()
            ap_list_xml = ap_list_response.text
            ap_list = APList(ap_list_xml)
            #print(ap_list)
            ap_data_list = []
            #ap_count_dict = {"count_up":{},"count_down":{}}
            zbx_items_ids = {"data_target": "zabbix_main","data_type": "items_ids","host_name":AW_HOSTNAME,
                             "host_id":host_id,"ip":AW_BASE_URL,"data": []}
            AP_PROCEDURE = PROCEDURE_AP(**{"aw_hostname":host_name,"aw_host_id":host_id})
            #"""
            with ThreadPoolExecutor(max_workers=10) as executor:
                try:
                    futures = [executor.submit(AP_PROCEDURE.process_ap, ap, interface_id, wap_dict_from_nb)
                               for ap in ap_list]
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            if result:
                                if result[0] == True:
                                    zbx_items_ids['data'].append(result[1])
                                    ap_data_list.append(result[3])
                                    result_count = result[2]
                                    if result_count['value'] == "UP":
                                        if result_count['floor'] in ap_count_dict['count_up']:
                                            ap_count_dict['count_up'][result_count['floor']] += 1
                                        else:
                                            ap_count_dict['count_up'][result_count['floor']] = 1
                                    elif result_count['value'] == "DOWN":
                                        if result_count['floor'] in ap_count_dict['count_down']:
                                            ap_count_dict['count_down'][result_count['floor']] += 1
                                        else:
                                            ap_count_dict['count_down'][result_count['floor']] = 1
                                    #if result_count['value'] == "UP":
                                    #    ap_count_dict['count_up'][result_count['floor']] += 1
                                    #elif result_count['value'] == "DOWN":
                                    #    ap_count_dict['count_down'][result_count['floor']] += 1
                        except Exception as err:
                            print(err)
                except Exception as err:
                    print(err)
            # Собираем все этажи из обоих словарей
            all_floors = set(ap_count_dict["count_up"].keys()).union(ap_count_dict["count_down"].keys())
            # Проверяем каждый этаж и добавляем отсутствующие с результатом 0
            for floor in all_floors:
                if floor not in ap_count_dict["count_up"]:
                    ap_count_dict["count_up"][floor] = 0
                if floor not in ap_count_dict["count_down"]:
                    ap_count_dict["count_down"][floor] = 0
            if ap_count_dict["count_down"] == {} or ap_count_dict["count_up"] == {}:
                return [False,None]
            count_data_list = AP_PROCEDURE.process_count_ap(ap_count_dict,wap_scope_name)
            for count_d in count_data_list[1]:
                zbx_items_ids['data'].append(count_d)

            #zabbix_items = zbx.get_all_items_in_host(host_id)
            #items_for_delete = AP_PROCEDURE.clear_extra_waste_items(**{"redis_data":zbx_items_ids['data'],"zbx_items":zabbix_items})
            #if items_for_delete[0] == True and items_for_delete[1] != []:
            #    for item_id in items_for_delete[1]:
            #        zbx.delete_item(item_id['itemid'])

            #    zbx_items_ids['data'] = items_for_delete[2]

            out_of_sync_aps_list = AP_PROCEDURE.unsync_data_between_nb_and_airwave(**{"wap_dict_from_nb":wap_dict_from_nb,"airwave_ap_list":ap_list})
            unsync_data_list = []
            if out_of_sync_aps_list[0] == True:
                zbx = ZBX_PROC()
                #data_list_out_of_sync = [{'ap_sn': 'CNH9K510QZ', 'host_name': 'wap-novator-0108'},
                #                         {'ap_sn': 'CNK2K513P1', 'host_name': 'wap-novator-0235'},
                #                         {'ap_sn': 'CNH5K5167N', 'host_name': 'wap-novator-0680'},
                #                         {'ap_sn': 'CNH5K515FX', 'host_name': 'wap-novator-0694'},
                #                         {'ap_sn': 'CNJLK510GH', 'host_name': 'wap-novator-0728'},
                #                         {'ap_sn': 'CNH5K511ZL', 'host_name': 'wap-novator-0844'}]
                for out_of_sync_item in out_of_sync_aps_list[1]:
                    try:
                        ap_name = out_of_sync_item.get('host_name', None)
                        ap_sn = out_of_sync_item.get('ap_sn', None)
                        if ap_name and ap_sn:
                            name_for_key = ap_name.replace("-","")
                            key = f"{name_for_key}.outofsync"
                            tags = [{'tag': 'name_of_ap', 'value': ap_name},{'tag': 'serial_number', 'value': ap_sn}]
                            for_create_item = {
                                "host_name": host_name,
                                "host_id": host_id,
                                "event_name": "data out of sync between nb and airwave",
                                "item_name": f"Out_of_sync -- {ap_name}",
                                "item_key": key,
                                "tags": tags, "value_type": 4, "item_type": 2,
                                "wap_name": ap_name,
                                "create_trigger": True,
                                "purpose_trigger": "Different",
                                "check_sn": False,
                                "host_sn_for_check": None,
                                "tags_for_trigger":[{"tag": "alarm_name","value":"WAP DATA UNSYNC"}]
                            }
                            zbx.create_item(**for_create_item)
                            unsync_data_list.append(f"{host_name} {key} 1")
                    except Exception as err:
                        print(err)

            return {"zbx_items_ids": zbx_items_ids, "sender_data_1": ap_data_list, "sender_data_2":count_data_list[0],"sender_data_3":unsync_data_list}
        else:
            return [False,None]


    except Exception as err:
        return [False,err]










