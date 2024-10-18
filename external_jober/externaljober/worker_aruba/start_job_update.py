
from airwaveapiclient import AirWaveAPIClient, APList


from externaljober.my_env import AW_API_LOGIN, AW_API_PASSWD
from externaljober.worker_aruba.mappings import ap_flours_count_list
from externaljober.zabbix.zabbix import ZBX_PROC
from externaljober.worker_aruba.proccess_wrk_update import PROCEDURE_AP
from externaljober.reddis.reddis_get import REDDIS



def start_update_process(wap_dict_from_nb ,AW_HOSTNAME):
    try:
        wap_scope_name = wap_dict_from_nb['wap_scope_hostname']
        #ap_count_dict = None
        #for ap_co in ap_flours_count_list:
        #    if ap_co["wap_scope_name"] == wap_scope_name:
         #       ap_count_dict = ap_co['count_dict']
        #if ap_count_dict:
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
        # print(ap_list)
        ap_data_list = []
        zbx_items_ids = {"data_target": "zabbix_main" ,"data_type": "items_ids" ,"host_name" :AW_HOSTNAME,
                         "host_id" :host_id ,"ip" :AW_BASE_URL ,"data": []}
        rediss = REDDIS()
        key_for_redis = f"externaljober:jober:scheduler:data:airwave:zbx:items:{AW_HOSTNAME}"
        redis_data = rediss.get_json(key_for_redis)
        AP_PROCEDURE = PROCEDURE_AP(**{"aw_hostname" :host_name ,"aw_host_id" :host_id})
        ap_proccess_result =  AP_PROCEDURE.process_ap(ap_list, wap_dict_from_nb, redis_data)
        ap_data_list = ap_proccess_result[0]
        ap_count_dict = ap_proccess_result[1]
        print(ap_count_dict)
        count_data_result = AP_PROCEDURE.process_count_ap(ap_count_dict, wap_scope_name,redis_data)
        return {"zbx_items_ids": None, "sender_data_1": ap_data_list, "sender_data_2": count_data_result}
        # send_to_zabbix_bulk(ZABBIX_SENDER_URL, ap_data_list)
        # time.sleep(5)
        # send_to_zabbix_bulk(ZABBIX_SENDER_URL, count_data_list[0])
        # print(result)
    # client.logout()
        #else:
        #    return [False, None]

        # """

    except Exception as err:
        return [False, err]








