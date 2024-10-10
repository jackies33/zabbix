


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



mcedit Dockerfile

_________________

FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "map_manager/core/main.py"]
_________________


docker build -t myapp:latest .


docker --version

docker-compose --version

mcedit requirements.txt
_________________
fastapi
uvicorn
pika
requests
pyzabbix
_________________

mcedit docker-compose.yml

_________________



version: '3.8'

services:
  zbx_map_manager:
    build: .
    container_name: zbx_map_manager
    networks:
      - app-network
    restart: always
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
    command: python map_manager/core/main.py

networks:
  app-network:
    driver: bridge


_________________

docker-compose build --no-cache
docker-compose up -d
docker ps

"""



import time
import datetime
from pytz import timezone
from fastapi import FastAPI, Response
import uvicorn
from concurrent.futures import ThreadPoolExecutor


from map_manager.core.discovery import START_DISCOVERY
from map_manager.core.get_data import GetData
from map_manager.core.tg_bot import telega_bot
from map_manager.my_env import server_port

i = 0

def start_job():
    get_data = GetData()
    all_maps = get_data.get_all_maps_from_zbx()
    for map in all_maps:
        starting = START_DISCOVERY(**{"essence": "MAP_Group", "essence_value": map})
        result = starting.start_proccess_discovery_main()
        tg_msg = f'Result from Map_Manager process for "{map}" = [{result[0]}] and not connected devices during execution = {result[1]}'
        tg = telega_bot()
        tg_send = tg.tg_sender(**{"message":tg_msg})

def run_webserver():
    app = FastAPI()
    uvicorn.run(app, host="0.0.0.0", port=server_port)



if __name__ == "__main__":
    run_time = datetime.time(hour=23, minute=30, second=0)
    tz = timezone('Europe/Moscow')
    timenow = datetime.datetime.now(tz).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    executor = ThreadPoolExecutor(max_workers=10)
    while i == 0:
        executor.submit(run_webserver)
        #executor.submit(start_job)
        #start_job()
        i = 1

    while i == 1:
        now = datetime.datetime.now()
        if now.time() >= run_time:  # Проверяем, что текущее время >= 23:30
            executor.submit(start_job)  # Запускаем задание
            time.sleep(80000)  # Спим 22 часа, чтобы запускать задание только один раз в день
        else:
            time.sleep(120)  # Ждем 2 минуты перед следующей проверкой времени






