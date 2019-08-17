
import http.server
import socketserver
import cgi

PORT = 8001

class myHandler(http.server.BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		#self.wfile.write("Hello World !".encode())
		f = open('index1.html')
		self.wfile.write(f.read().encode())
		f.close()
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

			print(form)
			print("Your name is: %s" % form["username"].value)
			self.send_response(200)
			self.end_headers()
			self.wfile.write(str.encode("Thanks %s !" % form["username"].value))
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

