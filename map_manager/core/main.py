


"""
Example to create docker-compose container



mkdir -p /opt/rabbitmq_logs
chmod 777 /opt/rabbitmq_logs



sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker --version
docker-compose --version

mcedit Dockerfile

_________________
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
_________________


add all app files in derectory with Dockerfile

mcedit requirements.txt
_________________
fastapi
uvicorn
pika
requests
pyzabbix
_________________
docker build -t myapp:latest .

mcedit docker-compose.yml

_________________
version: '3.8'

services:
  zbx_alarm_logic:
    build: .
    container_name: zbx_alarm_logic
    environment:
      - RABBITMQ_HOST='10.50.164.38'
      - PEER_SERVER_URL='10.50.174.37:8055'
      - WEIGHT_SERVER=100
      - SERVER_PORT=8055
      - PEER_NODE_NAME="sdc"
      - NODE_NAME="kr01"
      - ZBX_API_URL="http://10.50.164.38:8282/api_jsonrpc.php"
      - ZBX_API_TOKEN='c433fa5605593dd9bd3c1607de703ed7ac37a1542dec070ee94dbbdb7ff30f2a'
      - ALARM_HOST_NAME="EXTERNAL_SYSTEM_ALARM_MANAGER"
    networks:
      - app-network
    volumes:
      - /opt/rabbitmq_logs:/var/log/rabbitmq
    ports:
      - "8055:8055"

networks:
  app-network:
    driver: bridge
_________________

docker-compose build --no-cache
docker-compose up -d
docker ps

"""
print("Начало выполнения main.py")


import time
import datetime
from pytz import timezone
import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

print("Начало выполнения импортов")
from map_manager.core.discovery import START_DISCOVERY
from map_manager.core.get_data import GetData
from map_manager.core.tg_bot import telega_bot

i = 0

print("Импорты выполнены")


def start_job():
    get_data = GetData()
    all_maps = get_data.get_all_maps_from_zbx()
    for map in all_maps:
        starting = START_DISCOVERY(**{"essence": "MAP_Group", "essence_value": map})
        result = starting.start_proccess_discovery_main()
        tg_msg = f'Result from Map_Manager process for "{map}" = [{result[0]}] and not connected devices during execution = {result[1]}'
        tg = telega_bot()
        tg_send = tg.tg_sender(**{"message":tg_msg})


if __name__ == "__main__":
    run_time = datetime.time(hour=23, minute=55, second=0)
    tz = timezone('Europe/Moscow')
    timenow = datetime.datetime.now(tz).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    while i == 0:
        start_job()
        i = 1

    while i == 1:
        now = datetime.datetime.now()
        if now.weekday() == 6 and now.time() >= run_time:
            start_job()
            time.sleep(7200)  # sleep for waiting other day, and don't let to make job again in the same day
        else:
            time.sleep(120)  # enough time for request , and also not so often


