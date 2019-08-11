import pika
import time
import logging

logging.basicConfig()

#connection = pika.BlockingConnection(pika.ConnectionParameters('172.20.0.2'))

time.sleep(10)

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

#print(connection)
#print(channel)

channel.queue_declare(queue='hello')

for i in range(50):
    channel.basic_publish(exchange='', routing_key='hello', body='python3 /home/valentin/test.py')
    #channel.basic_publish(exchange='', routing_key='hello', body='ls /home/')
    print(" [x] Sent message")
    #logging.info("*** Sent message")
    time.sleep(1)

connection.close()

