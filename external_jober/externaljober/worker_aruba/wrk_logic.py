

import datetime
import time

from pytz import timezone



from externaljober.worker_aruba.start_job_full import start_full_process
from externaljober.worker_aruba.start_job_update import start_update_process
from externaljober.worker_aruba.proccess_wrk_ssid_user_count import PROCEDURE_SSID
from externaljober.reddis.reddis_get import REDDIS
from externaljober.netbox.netbox_get import NetboxGet
from externaljober.zabbix.zbx_sender import send_to_zabbix_bulk
from externaljober.my_env import ZABBIX_SENDER_URL

class WRK_LOGIC():

    def __init__(self,queue_name,message):
        self.queue_name = queue_name
        self.message = message


    def worker_logic(self):
        for task in self.message['job_data']:
            try:
                tz = timezone('Europe/Moscow')
                timenow = datetime.datetime.now(tz).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timenow}  ----  start worker_logic")
                redis_call = REDDIS()
                if self.queue_name == "air_wave_apstatus_worker":
                    host_name = task.get('host_name',None)
                    job_name = task.get('job_name',None)
                    wap_scope_name = task.get("wap_scope_name", None)
                    key_redis_for_nb_collect_data = task.get("key_nb_collect_data", None)
                    key_redis_for_zbx_collect_data = task.get("key_zbx_collect_data", None)
                    if host_name and job_name and key_redis_for_zbx_collect_data and key_redis_for_nb_collect_data:
                        nb_call = NetboxGet()
                        if job_name == "aps_status_get_update":
                            nb_data = redis_call.get_json(key_redis_for_nb_collect_data)
                            result = start_update_process(nb_data, host_name)
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result["sender_data_1"])
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result["sender_data_2"])
                        elif job_name == "aps_data_collect_full":
                            nb_data = nb_call.get_wap_devices(**{"wap_scope_hostname":wap_scope_name})
                            result = start_full_process(nb_data, host_name)
                            redis_call.set_json(key_redis_for_zbx_collect_data, result["zbx_items_ids"])
                            redis_call.set_json(key_redis_for_nb_collect_data,nb_data)
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result["sender_data_1"])
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result["sender_data_2"])
                            if result['sender_data_3'] != []:
                                time.sleep(30)
                                send_to_zabbix_bulk(ZABBIX_SENDER_URL, result["sender_data_3"])

                elif self.queue_name == "mobility_master_worker":
                    host_name = task.get('host_name', None)
                    job_name = task.get('job_name', None)
                    key_redis_for_zbx_collect_data = task.get("key_zbx_collect_data", None)
                    proccess = PROCEDURE_SSID(host_name)
                    if job_name == "ssid_count_users_full":
                        result = proccess.get_ssid_user_count_full()
                        if result[0] == True:
                            result_dict = result[1]
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result_dict["sender_data_1"])
                            redis_call.set_json(key_redis_for_zbx_collect_data, result_dict["zbx_items_ids"])
                    elif job_name == "ssid_count_users_update":
                        result = proccess.get_ssid_user_count_update()
                        if result[0] == True:
                            result_dict = result[1]
                            send_to_zabbix_bulk(ZABBIX_SENDER_URL, result_dict["sender_data_1"])


                    else:
                        print([False,'UNFICIAL DATA in recieved Message from RabbitMQ!'])
                else:
                    print([False, 'Unrecognized queue!'])
            except Exception as err:
                print(False, err)





