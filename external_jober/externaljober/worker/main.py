
import time
from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import FastAPI
import uvicorn


from externaljober.rabbitmq.consumer_worker import consume_from_rabbitmq
from externaljober.my_env import rbq_queue_for_worker


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
        executor.submit(consume_from_rabbitmq, rbq_queue_for_worker)
        # executor.submit(consume_from_rabbitmq, rbq_queue_for_worker)

if __name__ == "__main__":

    start_threads()





