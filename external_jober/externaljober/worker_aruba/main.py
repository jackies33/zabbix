



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
CMD ["python", "map_manager/core/wrk_logic.py"]
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
    command: python map_manager/core/wrk_logic.py

networks:
  app-network:
    driver: bridge


_________________

docker-compose build --no-cache
docker-compose up -d
docker ps

"""






from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
import uvicorn
import time
import os


from externaljober.my_env import rbq_queue_for_worker_airwave
from externaljober.rabbitmq.consumer_airwave import consume_from_rabbitmq



web_server_port = os.getenv('web_server_port')

def run_webserver():
    while True:
        try:
            app = FastAPI()
            uvicorn.run(app, host="0.0.0.0", port=int(web_server_port))
        except Exception as e:
            print(f"'run_webserver' crashed with error: {e}. Restarting...")
            time.sleep(5)

def start_threads():
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(consume_from_rabbitmq, rbq_queue_for_worker_airwave)
        executor.submit(run_webserver)
        # executor.submit(consume_from_rabbitmq, rbq_queue_for_worker)


if __name__ == "__main__":
    start_threads()
