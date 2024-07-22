


'''
for daemon setup script
create  - >> "mcedit /etc/systemd/system/zbx_consumer.service"
copy in zbx_consumer.service ->>
_______________________________

[Unit]
Description=Listen and classifier web hooks from netbox App through RabbitMQ

[Service]
ExecStart=/usr/bin/python3 /opt/zabbix_custom/rabbitmq/main.py
StandardOutput=file:/var/log/rabbitmq/output_sys.log
StandardError=file:/var/log/rabbitmq/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in zbx_consumer.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable zbx_consumer.service
sudo systemctl start zbx_consumer.service

______________________________

<<--- run next commands

'''




from fastapi import FastAPI, Response
import time
import threading
import requests
import logging
import uvicorn
import argparse


from my_env import initial_role,peer_server_url,weight_server,server_port,rabbitmq_queue
from consumer import consume_from_rabbitmq


app = FastAPI()
initial_role = initial_role
last_heartbeat_time = time.time()
times_check = 2

role_lock = threading.Lock()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/rabbitmq/consumer_log.txt')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#stream_handler = logging.StreamHandler(sys.stdout)
#stream_handler.setLevel(logging.DEBUG)
#stream_handler.setFormatter(formatter)
#logger.addHandler(stream_handler)

@app.post("/heartbeat")
def heartbeat():
    global last_heartbeat_time
    last_heartbeat_time = time.time()
    return Response(status_code=200)

@app.get("/status")
def status():
    global initial_role
    with role_lock:
        current_role = initial_role
    return {"status": current_role}

def send_heartbeat():
    while True:
        global initial_role,times_check
        with role_lock:
            current_role = initial_role
            check_count = times_check
        if current_role == 'standby' and check_count > 0:
            try:
                response = requests.post(f'http://{peer_server_url}/heartbeat')
                if response.status_code != 200:
                    logger.debug(f"\nFailed to send heartbeat to peer server.\n")
                    with role_lock:
                        logger.debug(f"\nchange chack_time\n")
                        times_check = times_check - 1
            except requests.exceptions.RequestException:
                logger.debug(f"\nchange chack_time\n")
                logger.debug(f"\nPeer server is down or unreachable.\n")
                with role_lock:
                    times_check = times_check - 1
        elif current_role == 'standby' and check_count <= 0:
            logger.debug(f"\nchange status to active\n")
            with role_lock:
                initial_role = 'active'
                times_check = 2
        elif current_role == 'active':
            try:
                response = requests.post(f'http://{peer_server_url}/heartbeat')
                if response.status_code != 200:
                    logger.debug(f"\nFailed to send heartbeat to peer server.\n")
                elif response.status_code == 200 and weight_server == 50:
                    logger.debug(f"\nchange status to standby\n")
                    with role_lock:
                        initial_role = 'standby'
                        times_check = 2
                elif response.status_code == 200 and weight_server == 100:
                    pass
            except requests.exceptions.RequestException:
                logger.debug(f"\nPeer server is down or unreachable.\n")
            pass
        time.sleep(5)

def manage_consumer():
    global initial_role
    consumer_thread = None

    while True:
        with role_lock:
            current_role = initial_role
        if current_role == 'active':
            if consumer_thread is None or not consumer_thread.is_alive():
                consumer_thread = threading.Thread(target=consume_from_rabbitmq(rabbitmq_queue), daemon=True)
                consumer_thread.start()
        elif current_role == 'standby':
            if consumer_thread is not None and consumer_thread.is_alive():
                consumer_thread.join(timeout=1)
                consumer_thread = None
        time.sleep(2)

def run_webserver():
    uvicorn.run(app, host="0.0.0.0", port=server_port)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Consumer HA')
    parser.add_argument('--status', action='store_true', help='Check the status of both instances')

    args = parser.parse_args()

    if args.status:
        try:
            local_status = requests.get(f'http://127.0.0.1:{server_port}/status').json()['status']
        except requests.exceptions.RequestException:
            local_status = "unreachable"

        try:
            peer_status = requests.get(f'http://{peer_server_url}/status').json()['status']
        except requests.exceptions.RequestException:
            peer_status = "unreachable"

        print(f"kr01==[{peer_status}]==")
        print(f"sdc==[{local_status}]==")
    else:
        threading.Thread(target=run_webserver, daemon=False).start()
        threading.Thread(target=send_heartbeat, daemon=True).start()
        threading.Thread(target=manage_consumer, daemon=True).start()



