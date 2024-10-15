


import datetime
from pytz import timezone
import time
import json
from concurrent.futures import ThreadPoolExecutor



from externaljober.worker.mappings import MAPPINGS
from externaljober.rabbitmq.producer import rb_producer
from externaljober.my_env import rbq_producer_sender_route_key,rbq_producer_sender_exchange

class WRK_LOGIC():

    def __init__(self,queue_name,message):
        self.queue_name = queue_name
        self.message = message


    def worker_logic(self):
        try:
            tz = timezone('Europe/Moscow')
            timenow = datetime.datetime.now(tz).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timenow}  ----  start worker_logic")
            mappings = MAPPINGS()
            list_for_zbx_sender = []
            if self.queue_name == "zbx_external_jober_worker":
                template_name = self.message.get('template_name',None)
                job_name = self.message.get('job_name',None)
                hosts_zbx_data = self.message.get('hosts_zbx_data')
                if template_name and job_name and hosts_zbx_data:
                    with ThreadPoolExecutor(max_workers=30) as executor:
                        futures_list = []
                        for host in hosts_zbx_data:
                            future = executor.submit(mappings.connection_exec,**{"template_name": template_name, "job_name": job_name, "host_zbx_data": host})
                            futures_list.append(future)
                        for f in futures_list:
                            if f.result()[0] == True:
                                list_for_zbx_sender.append(f.result()[1])
                            elif f.result()[0] == False:
                                print(f.result()[1],f.result()[2])
                    message_to_rabbit = {"template_name":template_name,"job_name":job_name,"metrics":list_for_zbx_sender}
                    if isinstance(message_to_rabbit, dict):
                        #print(message_to_rabbit)
                        json_message = json.dumps(message_to_rabbit)
                        bytes_message = json_message.encode('utf-8')
                        #print(bytes_message)
                        rb_send = rb_producer(bytes_message,rbq_producer_sender_exchange,rbq_producer_sender_route_key)
                        if rb_send == True:
                            print(f"{timenow}  ----  Sent job {job_name}to RabbitMQ success.")
                #elif job_name == 'aps_status_get_update' or job_name == "aps_data_collect_full":#resend task
                #    job_name = self.message.get('job_name', None)
                #    json_message = json.dumps(self.message)
                #    bytes_message = json_message.encode('utf-8')
                #    rb_send = rb_producer(bytes_message, "air_wave_workers", "air_wave_apstatus_worker")
                #    if rb_send == True:
                #        print(f"{timenow}  ----  Sent job {job_name}to RabbitMQ success.")
                else:
                    print([False,'UNFICIAL DATA in recieved Message from RabbitMQ!'])
            #elif self.queue_name == "air_wave_apstatus_worker":#resend task
            #    job_name = self.message.get('job_name', None)
            #    json_message = json.dumps(self.message)
            #    bytes_message = json_message.encode('utf-8')
            #    rb_send = rb_producer(bytes_message, "air_wave_workers", "air_wave_apstatus_worker")
            #    if rb_send == True:
            #        print(f"{timenow}  ----  Sent job {job_name}to RabbitMQ success.")

            else:
                print([False, 'Unrecognized queue!'])
        except Exception as err:
            print(False, err)


