import pika
import time
import logging

import os

logging.basicConfig()

time.sleep(10)

#connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq:rabbitmq@rabbitmq'))

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

#print(connection)
#print(channel)

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print(" [x] Received command: %r" % (body,))
    received_cmd_result = os.popen(body.decode("utf-8")).read()
    print(received_cmd_result)
    #logging.info(" [x] Received %r" % (body,))
    time.sleep(5)

channel.basic_consume('hello', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()
    rmq_tools.console_log("*** Error: ", traceback.format_exc())

connection.close()

