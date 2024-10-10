



import time
import json
from concurrent.futures import ThreadPoolExecutor



from external_jober.externaljober.worker.mappings import MAPPINGS
from external_jober.externaljober.rabbitmq.producer import rb_producer
from external_jober.externaljober.my_env import rbq_producer_sender_route_key,rbq_producer_sender_exchange


class WRK_LOGIC():

    def __init__(self,queue_name,message):
        self.queue_name = queue_name
        self.message = message


    def worker_logic(self):
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
                        if f[0] == True:
                            list_for_zbx_sender.append(f[1])
                        elif f[0] == False:
                            print(f[1],f[2])
                message_to_rabbit = {"template_name":template_name,"job_name":job_name,"metrics":list_for_zbx_sender}
                if isinstance(message_to_rabbit, dict):
                    print(message_to_rabbit)
                    json_message = json.dumps(message_to_rabbit)
                    bytes_message = json_message.encode('utf-8')
                    print(bytes_message)
                    rb_send = rb_producer(bytes_message,rbq_producer_sender_exchange,rbq_producer_sender_route_key)
                    if rb_send == True:
                        print(f"Sent job {job_name}to RabbitMQ success.")

            else:
                print([False,'UNFICIAL DATA in recieved Message from RabbitMQ!'])
        else:
            print([False, 'Unrecognized queue!'])





#if __name__ == "__main__":
#    my_queue = "zbx_external_jober_worker"
#    my_dict = {'template_name': 'Atlas.OS dwdm', 'interval': 180, 'job_name': 'dwdm_optic_ifaces_metrics_get', 'hosts_zbx_data': [{'hostid': '13031', 'name': 'dwdm-krasnogorsk-kr01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.157', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13695', 'name': 'dwdm-istra-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.148', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13209', 'name': 'kr01-mus-dwdm', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.50.71.9', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13527', 'name': 'sdc-mus-dwdm', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.50.61.9', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13038', 'name': 'dwdm-domodedovo-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.12', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13042', 'name': 'dwdm-vidnoe-02', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.5', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13035', 'name': 'dwdm-vidnoe-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.4', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13036', 'name': 'dwdm-pushcino-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.60', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13034', 'name': 'dwdm-podolsk-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.136.5', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13052', 'name': 'dwdm-odincovo-02', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.85', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13046', 'name': 'dwdm-odincovo-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.84', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13047', 'name': 'dwdm-lyubercy-02', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.136.69', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13053', 'name': 'dwdm-lyubercy-01', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.136.68', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13391', 'name': 'm9-mus-dwdm', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.50.91.9', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}, {'hostid': '13055', 'name': 'dwdm-krasnogorsk-sdc', 'parentTemplates': [{'templateid': '16248', 'name': 'Atlas.OS dwdm'}], 'groups': [{'groupid': '30', 'name': 'T8/Atlas.OS/T6-10EP-DCI-01'}], 'interfaces': [{'ip': '10.100.137.156', 'details': {'version': '2', 'bulk': '1', 'community': 'n0cdwdm', 'max_repetitions': '3'}}]}], 'job_number': '1'}
#    WRK = WRK_LOGIC(my_queue,my_dict)
#    result = WRK.worker_logic()
