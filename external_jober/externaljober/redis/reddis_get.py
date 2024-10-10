
import redis
import json


from external_jober.externaljober.my_env import REDDIS_URL, REDDIS_PORT



class REDDIS_GET():
    def __init__(self):
        self.r = redis.Redis(host=REDDIS_URL, port=REDDIS_PORT)

    def reddis_get(self,key):
        # Подключение к Redis
        # Получение конфигурации задачи с использованием JSON.GET
        job_config = self.r.execute_command("JSON.GET", key)

        if job_config:
            job_config = json.loads(job_config)
            #print(job_config)  # {'device': 'router1', 'interval': 60, 'type': 'poll'}
            return job_config
        else:
            #print("No data found for the specified key.")
            return None

    def reddis_get_all_by_prefix(self, prefix):
        # Найти все ключи, начинающиеся с заданного префикса
        keys = self.r.scan_iter(f"{prefix}*")
        all_data = []

        for key in keys:
            # Получение данных по каждому ключу с использованием JSON.GET
            try:
                job_config = self.r.execute_command("JSON.GET", key)
                if job_config:
                    job_config = json.loads(job_config)
                    all_data.append(job_config)
            except redis.exceptions.ResponseError as e:
                print(f"Error retrieving JSON for key {key}: {e}")

        return all_data


#redis-cli JSON.SET externaljober:jober:scheduler:tasks:bytemplatesname . '[{"template_name": "Atlas.OS dwdm", "interval": 180, "type": "poll", "job_name":"dwdm_optic_ifaces_metrics_get"}'

#redis-cli JSON.SET externaljober:jober:scheduler:tasks:templatesname:atlasosdwdm:1 . '{"device": "router1", "interval": 60, "type": "poll"}'