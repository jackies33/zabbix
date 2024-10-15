
import redis
import json


from externaljober.my_env import REDDIS_URL, REDDIS_PORT



class REDDIS_GET():
    def __init__(self):
        self.r = redis.Redis(host=REDDIS_URL, port=REDDIS_PORT)

    def reddis_get_config(self,key):
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

    def set_json(self, key, data_dict):
        # Сериализуем словарь в JSON
        json_data = json.dumps(data_dict)
        # Используем JSON.SET команду для сохранения в Redis
        self.r.execute_command('JSON.SET', key, '.', json_data)
        return True

    def get_json(self, key):
        data = self.r.execute_command("JSON.GET", key)
        if data:
            return json.loads(data)
        else:
            return None

