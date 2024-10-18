



from externaljober.reddis.reddis_get import REDDIS
from externaljober.my_env import redis_configs_list_for_jobs
from externaljober.zabbix.zabbix import ZBX_PROC

def poll_redis(prefix):#key
    reddis_Get = REDDIS()
    #redis_get_result = reddis_Get.reddis_get(key)
    redis_get_result = reddis_Get.reddis_get_all_by_prefix(prefix)
    if redis_get_result:
        return redis_get_result

def exec_get_redis():
    list_redis_configs = []
    for key in redis_configs_list_for_jobs:
        result_from_redis = poll_redis(key)
        if result_from_redis:
            for r in result_from_redis:
                list_redis_configs.append(r)
    return list_redis_configs



class PARSE_DATA_ZBX():

    def __init__(self,get_type):
        self.get_type = get_type


    def get_zbx_data(self,configs_list):
        job_number = 0
        zbx_get = ZBX_PROC()
        job_list = []
        if self.get_type == "bytemplate":
            for config in configs_list:
                template_id = zbx_get.get_template_id(config['template_name'])
                hots_zbx_data = zbx_get.get_hosts_by_template(template_id)
                job_number = job_number + 1
                job_list.append({
                    'template_name': config['template_name'], 'interval': config['interval'],  'job_name': config['job_name'],
                     'hosts_zbx_data':hots_zbx_data, 'job_number':str(job_number),'rb_route_key':config['rb_route_key'], 'rb_exchange':config['rb_exchange']
                    }
                )
        return job_list

