

import datetime
from pytz import timezone



from externaljober.worker_aruba.start_job_full import start_full_process
from externaljober.worker_aruba.start_job_update import start_update_process
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
                if self.queue_name == "air_wave_apstatus_worker":
                    host_name = task.get('host_name',None)
                    job_name = task.get('job_name',None)
                    wap_scope_name = task.get("wap_scope_name", None)
                    key_redis_for_nb_collect_data = task.get("key_nb_collect_data", None)
                    key_redis_for_zbx_collect_data = task.get("key_zbx_collect_data", None)
                    if host_name and job_name and key_redis_for_zbx_collect_data and key_redis_for_nb_collect_data:
                        redis_call = REDDIS()
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

                    else:
                        print([False,'UNFICIAL DATA in recieved Message from RabbitMQ!'])
                else:
                    print([False, 'Unrecognized queue!'])
            except Exception as err:
                print(False, err)





