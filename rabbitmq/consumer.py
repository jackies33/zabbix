


import pika
import time
import json
import sys
import logging


from my_env import rabbitmq_host, rabbitmq_queue, rbq_producer_pass, rbq_producer_login, my_path_sys
sys.path.append(my_path_sys)

from remote_system.core.handler_core import Handler_WebHook



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


def callback(ch, method, properties, body):
    data_for_sent = json.loads(body.decode())
    data = {"data_type": "netbox_main", "data": data_for_sent}
    call = Handler_WebHook()
    print(data)
    result = call.core_handler(**data)
    try:
        for r in result:
            logger.debug(f"\n{r}\n")
            #print(r)
    except Exception as err:
        logger.debug(f"\n{err}\n")
        #print(err)
    #print(f"Received message: {body.decode()}")

def consume_from_rabbitmq(queue_name):
    try:
        #print("trying to recieve a meassage from RabbitMQ...")
        credentials = pika.PlainCredentials(rbq_producer_login, rbq_producer_pass)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials
        ))
        channel = connection.channel()
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
        logger.debug(f"\nConnection to RabbitMQ is OK\n")
        if method_frame:
            callback(channel, method_frame, header_frame, body)
        else:
            pass

        connection.close()
    except pika.exceptions.AMQPConnectionError:
        logger.debug(f"\nConnection to RabbitMQ failed, retrying...\n")
        #print("Connection to RabbitMQ failed, retrying...")

#if __name__ == "__main__":
#    while True:
#        consume_from_rabbitmq(rabbitmq_queue)
#        time.sleep(1)  # Wait for 2 seconds before checking the queue again

