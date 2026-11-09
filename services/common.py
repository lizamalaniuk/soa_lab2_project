import json
import os
import time
import pika
import redis

INSTANCE = os.environ.get("HOSTNAME", "unknown")

def db():
    return redis.Redis(host="redis", port=6379, decode_responses=True)

def publish(event_type, payload):
    params = pika.ConnectionParameters(host="rabbitmq", heartbeat=30, blocked_connection_timeout=10)
    for attempt in range(10):
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(exchange="homework.events", exchange_type="fanout", durable=True)
            channel.queue_declare(queue="notification.events", durable=True)
            channel.queue_bind(exchange="homework.events", queue="notification.events")
            channel.basic_publish(exchange="homework.events", routing_key="", body=json.dumps({"type": event_type, "data": payload}), properties=pika.BasicProperties(delivery_mode=2))
            connection.close()
            return
        except pika.exceptions.AMQPConnectionError:
            if attempt == 9:
                raise
            time.sleep(1)
