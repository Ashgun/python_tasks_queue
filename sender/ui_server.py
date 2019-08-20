
import http.server
import socketserver
import cgi

import pika
import time
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

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
	header_row = ['Command',   'Status',   'Output', 'Message']
	html = '<table border="1"><tr><th>' + '</th><th>'.join(header_row) + '</th></tr>'

	for task in db.posts.find({}):
		command = '<td>' + task['command'] + '</td>'
		status = '<td bgcolor="' + status_color_map[task['status']] + '">' + task['status'] + '</td>'
		output = '<td>' + task['output'].strip().replace('\\n', '<br>') + '</td>'
		message = '<td>' + task['message'].strip().replace('\c\n', '<br>') + '</td>'
		row = [command, status, output, message]
		html += '<tr>' + "".join(row) + '</tr>'
	html += '</table>'

	return html

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
			print("self.rfile", self.rfile);
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
    
			print(" [x] Sent message")
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

