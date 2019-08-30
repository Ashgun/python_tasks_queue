
import http.server
import socketserver
import cgi

import pika
import time
import json
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

import urllib.parse as urlparse

logging.basicConfig()

time.sleep(15)

client = MongoClient('mongodb://mongodb:27017/')
db = client['commands_data']

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.queue_declare(queue='hello')

PORT = 8001

status_color_map = {
	'done': '#00ff00',
	'failed': '#ff0000',
	'open': '#f0f0f0',
	'in progress': '#ffbf00'
}

def GetTasksList():
	result = { "tasks" : [] };
	for task in db.posts.find({}):
		taskView = {
			"id" : str(task['_id']),
			"message" : task['message'].strip().replace('\\n', '<br>').replace('\n', '<br>'),
			"output" : task['output'].strip().replace('\\n', '<br>').replace('\n', '<br>'),
			"status" : task['status'],
			"command" : task['command'],
			"color" : status_color_map[task['status']]
		}

		result["tasks"].append(taskView)

	return json.dumps(result)

def GetTaskById(uid):
	for task in db.posts.find({'_id': ObjectId(uid)}):
		taskView = {
			"obtainedId" : str(task['_id']),
			"message" : task['message'].strip().replace('\\n', '<br>').replace('\n', '<br>'),
			"output" : task['output'].strip().replace('\\n', '<br>').replace('\n', '<br>'),
			"status" : task['status'],
			"command" : task['command'],
			"color" : status_color_map[task['status']]
		}
		return json.dumps(taskView)

	data = { 'obtainedId' : uid }
	return json.dumps(data)

class myHandler(http.server.BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		#print("GET", self.path)
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			# Send the html message
			#self.wfile.write("Hello World !".encode())
			f = open('index.html')
			self.wfile.write(f.read().encode())
			f.close()

		if self.path.startswith('/get_record'):
			form = urlparse.parse_qs(urlparse.urlparse(self.path).query)

			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(GetTaskById(form['id'][0]).encode())

		if self.path == '/status':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			#self.wfile.write((str(time.clock()) + '<br>Status<br>information').encode())

			self.wfile.write(GetTasksList().encode())
			#print(GetTasksList())

		return
	def do_POST(self):
		print("POST", self.path)
		if self.path=="/send":
			#print("self.rfile", self.rfile);
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			#print(form)
			#print("Your name is: %s" % form["username"].value)
			self.send_response(200)
			self.end_headers()
			#self.wfile.write(str.encode("Thanks %s !" % form["username"].value))

			post = {
				'command': form["cmdText"].value,
				'status': 'open',
				'output': '',
				'message': ''
			}
			post_id = db.posts.insert_one(post).inserted_id

			channel.basic_publish(exchange='', routing_key='hello', body=str(post_id))
			#channel.basic_publish(exchange='', routing_key='hello', body='ls /home/')
    
			print(" [x] Sent command to queue")
		return	


try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = socketserver.TCPServer(('', PORT), myHandler)
	print('Started httpserver on port ' , PORT)
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print('^C received, shutting down the web server')
	server.socket.close()

