


import time
from concurrent.futures import ThreadPoolExecutor


from external_jober.externaljober.rabbitmq.consumer_worker import consume_from_rabbitmq
from external_jober.externaljober.my_env import rbq_queue_for_worker


def start_threads():
    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(consume_from_rabbitmq,rbq_queue_for_worker)
    executor.submit(consume_from_rabbitmq, rbq_queue_for_worker)


if __name__ == "__main__":
    start_threads()