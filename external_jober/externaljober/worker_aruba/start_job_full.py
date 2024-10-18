



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
                    futures = [executor.submit(AP_PROCEDURE.process_ap, ap, interface_id, ap_data_list, wap_dict_from_nb)
                               for ap in ap_list]
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            if result:
                                if result[0] == True:
                                    zbx_items_ids['data'].append(result[1])
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
            print(ap_count_dict)
            count_data_list = AP_PROCEDURE.process_count_ap(ap_count_dict,wap_scope_name)
            for count_d in count_data_list[1]:
                zbx_items_ids['data'].append(count_d)
            return {"zbx_items_ids": zbx_items_ids, "sender_data_1": ap_data_list, "sender_data_2":count_data_list[0]}
        else:
            return [False,None]


    except Exception as err:
        return [False,err]










