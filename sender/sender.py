import pika
import time
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

logging.basicConfig()

#connection = pika.BlockingConnection(pika.ConnectionParameters('172.20.0.2'))

time.sleep(10)

client = MongoClient('mongodb://mongodb:27017/')
db = client['commands_data']

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

#print(connection)
#print(channel)

channel.queue_declare(queue='hello')

for i in range(50):
    post = {
            'command': 'python3 /home/valentin/test.py',
            'status': 'open',
            'output': '',
            'message': ''
    }
    posts = db.posts
    post_id = posts.insert_one(post).inserted_id
    #print(post_id)
    #print(str(posts.find_one()['_id']))
    
    channel.basic_publish(exchange='', routing_key='hello', body=str(post_id))
    #channel.basic_publish(exchange='', routing_key='hello', body='ls /home/')
    
    print(" [x] Sent message")
    #logging.info("*** Sent message")
    time.sleep(1)

connection.close()

