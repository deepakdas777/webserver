import socket
import sys
import os
import time

class HttpServer:
	
	def __init__(self, port=8080):
		''' http server constructor'''	
		self.port = port
		self.host_dir = '.' 
		self.ip_address = '127.0.0.1'
		self.max_connections=10
	
	def get_content_type(self, file_name):
		''' this method extract the file type from the file name'''
		content_types = {'html': 'text/html',
						'txt': 'text/txt',
						'jpg': 'image/jpeg',
						'png': 'image/png',
						'ico': 'icon/ico',
						'pdf': 'application/pdf',
						'gif': 'image/gif'}
		return content_types[file_name.split('.')[-1]]
	def make_header(self, http_code, content_type):
		''' return the header for the response'''
		headr = ''
		if(http_code == 200):
			headr = 'HTTP/1.1 200 OK\n'
		elif(http_code == 404):
			headr = 'HTTP/1.1 404 File Not Found\n'
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		headr += 'Date:' + date + '\n'
		headr += 'Server: Python-http-server\n'
		headr += 'Content-Type:'+ content_type + '\n'
		headr += '\n'
		return headr


	def create_socket(self):
		'''  creating server socket'''
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.server.bind((self.ip_address, self.port))
			print("Starting up http-server, serving ./")
			print("Available on\n http://127.0.0.1:%d"%self.port)
			print("Hit CTRL-C to stop the server")
		except:
			self.port += 1
			self.create_socket()
		self.listen()

	def listen(self):
		''' listening for new connection '''
		while True:
			print("Waiting for new connection\n")
			self.server.listen(self.max_connections)
			print('Parent PID : {pid}\n'.format(pid=os.getpid()))
			client_connection, address =  self.server.accept()
			pid = os.fork()
			if(pid == 0):
				self.server.close()
				self.handle_request(client_connection, address)
				client_connection.close()
				os.exit(0)
			else:
				client_connection.close()

	def handle_request(self, client_connection, address):
		'''handling request from the client''' 
		requested_data = client_connection.recv(1024)
		print("Recived connection from:",address)
		requested_string = bytes.decode(requested_data)
		requested_method = requested_string.split(' ')[0]
		print("Request method:",requested_method)
		print("Request content:\n",requested_string)
		if(requested_method == 'GET'):
			requested_file = requested_string.split(' ')[1]
			if(requested_file == '/'):
				requested_file = '/index.html'
			requested_file = self.host_dir + requested_file
			try:
				fp = open(requested_file, 'rb')
				response_data = fp.read()
				fp.close()
				content_type = self.get_content_type(requested_file)
				header = self.make_header(200, content_type)
			except:
				header = self.make_header(404, 'text/html')
				response_data = b'<html><body><p> Error 404 File not found</p></body></html>'
			final_response = header.encode()
			final_response += response_data
			print("Serving:",requested_file)
			client_connection.send(final_response)				  
			time.sleep(50)
			
		else:
			print(requested_method)
			print("HTTP request method unknown")			
			
	
			

		
new_server = HttpServer()
new_server.create_socket()


