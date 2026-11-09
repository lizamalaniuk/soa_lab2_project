import json,time,pika
from common import db
while True:
    try:
        connection=pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq',heartbeat=30))
        ch=connection.channel()
        ch.exchange_declare(exchange='homework.events',exchange_type='fanout',durable=True)
        ch.queue_declare(queue='notification.events',durable=True)
        ch.queue_bind(exchange='homework.events',queue='notification.events')
        def callback(channel,method,properties,body):
            event=json.loads(body)
            data=event['data']
            message={'event':event['type'],'homework_id':data['id'],'user_id':data['user_id'],'message':('Завдання створено: '+data['subject']) if event['type']=='homework.created' else ('Завдання виконано: '+data['subject'])}
            db().lpush('notifications',json.dumps(message,ensure_ascii=False))
            print('CONSUMED:',message,flush=True)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(queue='notification.events',on_message_callback=callback)
        print('Notification consumer started',flush=True)
        ch.start_consuming()
    except Exception as exc:
        print('Consumer reconnect:',str(exc),flush=True)
        time.sleep(3)
