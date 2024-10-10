




import pika

from external_jober.externaljober.my_env import rabbitmq_host, rbq_producer_pass,rbq_producer_login

def rb_producer(message,rbq_producer_exchange,rbq_producer_route_key):
    credentials = pika.PlainCredentials(rbq_producer_login, rbq_producer_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host,credentials=credentials))
    channel = connection.channel()
    channel.basic_publish(
        exchange=rbq_producer_exchange,
        routing_key=rbq_producer_route_key,
        body=message
    )

    connection.close()
    return True
