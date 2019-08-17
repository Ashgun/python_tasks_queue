import pika
import time
import logging

import os

from pymongo import MongoClient
from bson.objectid import ObjectId

import subprocess

logging.basicConfig()

print('WORKER_ID = ', os.environ['WORKER_ID'])

client = MongoClient('mongodb://mongodb:27017/')
db = client['commands_data']

time.sleep(20)


#connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq:rabbitmq@rabbitmq'))

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

#print(connection)
#print(channel)

channel.queue_declare(queue='statuses')

def callback(ch, method, properties, body):
    posts = db.posts
    uid = body.decode("utf-8")

    command_data = posts.find_one({'_id': ObjectId(uid)})
    #print(command_data)
    cmd = command_data['command']
    status = command_data['status']

    if status == 'open':
        print(" [x] Received command: %s" % (cmd,))

        try:
            #received_cmd_result = os.popen(cmd).read()
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            #print(received_cmd_result)
            output, error = process.communicate()
            #print(output, error)
            received_cmd_result = str(output)[2:-1]
            error_message = str(error)[2:-1]

            new_status = 'done' if not error_message else 'failed'

            #print(received_cmd_result, error_message, new_status, len(error_message))

            posts.update_one({'_id': ObjectId(uid)}, {'$set': {'status': new_status, 'output': received_cmd_result, 'message': error_message}})

            channel.basic_publish(exchange='', routing_key='statuses', body=str({'id': uid, 'status': new_status, 'output': received_cmd_result, 'message': error_message}))

        except Exception as e:
            print('*** Exception: ', str(e))
            new_status = 'failed'
            message = str(e)
            posts.update_one({'_id': ObjectId(uid)}, {'$set': {'status': new_status, 'output': '', 'message': message}})

            channel.basic_publish(exchange='', routing_key='statuses', body=str({'id': uid, 'status': new_status, 'message': message}))
    
    time.sleep(1)

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

