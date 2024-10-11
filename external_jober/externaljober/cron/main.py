

from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
import uvicorn
import time
import json


from externaljober.my_env import web_server_port,rbq_producer_worker_exchange,rbq_producer_worker_route_key
from externaljober.cron.parse_data import get_and_parse_redis_configs
from externaljober.rabbitmq.producer import rb_producer

configs_redis = []


def run_webserver():
    while True:
        try:
            app = FastAPI()
            uvicorn.run(app, host="0.0.0.0", port=web_server_port)
        except Exception as e:
            print(f"'run_webserver' crashed with error: {e}. Restarting...")
            time.sleep(5)


def run_get_configs_redis():
    while True:
        try:
            global configs_redis
            #print(configs_redis)
            configs_redis = get_and_parse_redis_configs()

            #print(configs_redis)
            time.sleep(300)
        except Exception as e:
            print(f"'run_get_configs_redis' method crashed with error: {e}. Restarting...")
            time.sleep(5)


def scheduler_tasks():
    while True:
        try:
            global configs_redis
            if configs_redis != []:
                current_time = time.time()
                for task in configs_redis:
                    task_last_run = task.get("last_run", None)
                    if task_last_run:
                        """
                        if isinstance(task, dict):
                            print(task)
                            json_message = json.dumps(task)
                            bytes_message = json_message.encode('utf-8')
                            print(bytes_message)
                            rb_send = rb_producer(bytes_message,rbq_producer_worker_exchange,rbq_producer_worker_route_key)
                            if rb_send == True:
                                print(f"Sent job {task['job_name']}to RabbitMQ success.")
                        """
                        # Проверяем, истёк ли интервал задачи
                        if current_time - task_last_run >= task["interval"]:
                            #print(task)
                            print(f"Interval reached for {task['job_name']}. Sending to RabbitMQ.")
                            if isinstance(task, dict):
                                print(task)
                                json_message = json.dumps(task)
                                bytes_message = json_message.encode('utf-8')
                                print(bytes_message)
                                rb_send = rb_producer(bytes_message,rbq_producer_worker_exchange,rbq_producer_worker_route_key)
                                if rb_send == True:
                                    print(f"Sent job {task['job_name']}to RabbitMQ success.")
                            # Обновляем время последнего запуска
                            task["last_run"] = current_time
                        elif current_time - task_last_run < task['interval']:
                            pass
                            #print(current_time)
                            #print(task['last_run'])
                            #print(f"Interval not reached yet for {task['job_name']}. Skipping task.")
                    elif not task_last_run:
                        #print(task)
                        print(f"Interval reached for {task['job_name']}. Sending to RabbitMQ.")
                        print(task)
                        if isinstance(task, dict):
                            json_message = json.dumps(task)
                            bytes_message = json_message.encode('utf-8')
                            print(bytes_message)
                            rb_send = rb_producer(bytes_message,rbq_producer_worker_exchange,rbq_producer_worker_route_key)

                            if rb_send == True:
                                print(f'Sent job "{task["job_name"]}" to RabbitMQ success.')
                        task.update({"last_run":current_time})
                time.sleep(5)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"'check_tasks' method crashed with error: {e}. Restarting...")
            time.sleep(5)



if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=10)
    executor.submit(run_webserver)
    executor.submit(run_get_configs_redis)
    executor.submit(scheduler_tasks)
















