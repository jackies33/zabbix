


import time
from concurrent.futures import ThreadPoolExecutor
import uvicorn
from fastapi import FastAPI
from kafka import KafkaConsumer
import sys
import uuid


from my_env import server_port,target_ip,kafka_fqdn,kafka_consumer_topic
from event_manager import event_manager



def print_to_stdout(message):
    sys.stdout.write(message + '\n')
    sys.stdout.flush()



def parse_as_path_change_from_peers():
    my_group_id = f"my-consumer-group-{uuid.uuid4()}"
    consumer = KafkaConsumer(
        kafka_consumer_topic,
        bootstrap_servers=kafka_fqdn,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        consumer_timeout_ms=999999999,
        group_id=my_group_id
    )
    print_to_stdout(my_group_id)
    print_to_stdout(f"Consumer connected to topic: {consumer.subscription()}")
    for message in consumer:
        try:
            raw_message = message.value.decode('utf-8')
            message_parts = raw_message.split('\t')
            data = {
                #"source_router_ip":message_parts[4],
                #"peer_ip":message_parts[6],
                #"time":message_parts[8],
                #"as_path":message_parts[10],
                "source_router_ip": message_parts[4],
                "peer_ip": message_parts[7],
                "time": message_parts[9],
                "as_path": message_parts[14],
            }
            #print_to_stdout(f"Structured data:, {data}")
            for t_ip in target_ip:
                if data['peer_ip'] == t_ip:
                    print_to_stdout(f"Structured data:, {data}")
                    event_manager(**data)


        except Exception as e:
            print_to_stdout(f"Error processing message: {e}")
    consumer.close()

def start_job():
    while True:
        parse_as_path_change_from_peers()
        time.sleep(3)

def run_webserver():
    # Инициализация веб-сервера FastAPI
    app = FastAPI()
    @app.get("/")
    def read_root():
        return {"message": "Server is running"}

    uvicorn.run(app, host="0.0.0.0", port=server_port)

if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(run_webserver)
    #executor.submit(start_job)
    start_job()





