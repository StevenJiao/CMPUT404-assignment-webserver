#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def getDataFromUri(self, folder_name, uri):
        file_name = os.path.join(folder_name, uri).rstrip('/')
        print("file name:", file_name)
        if not os.path.isfile(file_name):
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))
            return
        with open(file_name, 'rb') as f:
            data = f.read()
        return data
    
    def handle(self):
        # get the data portion oft he request
        self.data = self.request.recv(1024).strip()
        print("Request data: %s\n" % self.data)

        # split data by return and new line
        lines = self.data.split(bytearray("\r\n", 'utf-8'))

        # split the first line of data to get the method, uri, and http version
        request_line = lines[0].decode()
        if len(request_line.split(' ')) == 3:
            method, uri, http_version = request_line.split(' ')
            print("Method:", method, ", Uri:", uri, ", http_version:", http_version)
        else:
            return

        # if the method is not GET, send a Method Not Allowed message
        if method != 'GET':
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", 'utf-8'))

        # see if we're provided an index.html filename or not
        if ('.' not in uri.split('/')[-1]):
            if (not uri.endswith('/')):
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: " + uri + "/\r\n\r\n", 'utf-8'))
                return
            uri += "/index.html"

        # get the data and send it
        uri_data = self.getDataFromUri("www", uri.strip('/'))

        if uri_data:
            content_type = "text/css" if uri.endswith(".css") else "text/html" 
            header = bytearray("HTTP/1.1 200 OK\r\nContent-Type: " + content_type + "\r\n", 'utf-8')
            self.request.sendall(header + bytearray("\r\n", 'utf-8') + uri_data + bytearray("\r\n", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
