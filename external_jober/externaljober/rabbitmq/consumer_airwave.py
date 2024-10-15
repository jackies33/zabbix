import time

import pika
import json

from externaljober.my_env import rabbitmq_host, rbq_producer_pass, rbq_producer_login
from externaljober.worker_aruba.aruba_ap_status.wrk_logic import WRK_LOGIC


def process_message(queue_name, message_body):
    try:
        message = json.loads(message_body)
        print(f"Received message from {queue_name}: {message}")
        #time.sleep(10)
        WRK = WRK_LOGIC(queue_name, message)
        WRK.worker_logic()
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from {queue_name}: {message_body}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def on_message_callback(ch, method, properties, body):
    print(f"Processing message from queue: {method.routing_key}")
    process_message(method.routing_key, body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_from_rabbitmq(queue_name):
    while True:
        try:
            credentials = pika.PlainCredentials(rbq_producer_login, rbq_producer_pass)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=rabbitmq_host,
                credentials=credentials
            ))
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=False)
            print(f"Start listening on queue: {queue_name}")
            channel.start_consuming()

        except Exception as e:
            print(f"Error connecting to RabbitMQ {queue_name}: {e}")