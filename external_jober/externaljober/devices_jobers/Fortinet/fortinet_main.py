




from externaljober.my_env import redis_keys_for_hosts
from externaljober.reddis.reddis_get import REDDIS_GET

class FortiNetApi():
    def __init__(self, **kwargs):
        self.data = kwargs
        ip = kwargs['interfaces'][0]['ip']
        host_name = kwargs['name']
        self.FORTIGATE_IP = ip
        redis = REDDIS_GET()
        self.FORTI_API_TOKEN = redis.reddis_get(f"{redis_keys_for_hosts}:fortinet:{host_name}:apikey")
        self.headers = {
            "Authorization": f"Bearer {self.FORTI_API_TOKEN}",
            "Content-Type": "application/json"
        }





