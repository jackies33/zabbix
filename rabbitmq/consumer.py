




'''
for daemon setup script
create  - >> "mcedit /etc/systemd/system/rs_zbx.service"
copy in rs_zbx.service ->>
_______________________________

[Unit]
Description=Listen and classifier web hooks from netbox App through RabbitMQ

[Service]
ExecStart=/usr/bin/python3 /opt/zabbix1/rabbitmq/consumer.py
StandardOutput=file:/var/log/rs_zbx/output.log
StandardError=file:/var/log/rs_zbx/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in rs_zbx.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable rs_zbx.service
sudo systemctl start rs_zbx.service

______________________________

<<--- run next commands

'''



import pika
import time
import json
import sys

from my_env import rabbitmq_host,rabbitmq_queue, my_path_sys
sys.path.append(my_path_sys)

from remote_system.core.handler_core import Handler_WebHook



def callback(ch, method, properties, body):
    data_for_sent = json.loads(body.decode())
    data = {"data_type": "netbox_main", "data": data_for_sent}
    call = Handler_WebHook()
    result = call.core_handler(**data)
    try:
        for r in result:
            print(r)
    except Exception as err:
        print(err)
    #print(f"Received message: {body.decode()}")

def consume_from_rabbitmq(queue_name):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
        if method_frame:
            callback(channel, method_frame, header_frame, body)
        else:
            pass

        connection.close()
    except pika.exceptions.AMQPConnectionError:
        print("Connection to RabbitMQ failed, retrying...")

if __name__ == "__main__":
    while True:
        consume_from_rabbitmq(rabbitmq_queue)
        time.sleep(1)  # Wait for 2 seconds before checking the queue again

