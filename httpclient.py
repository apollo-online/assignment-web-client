#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse # changed

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port): # establish connection with server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data): # helper for getting response code after sending request to server
        return data.split(' ')[1] # return the response code
        
    def get_headers(self,data): # not needed?
        return None 

    def get_body(self, data): # not needed?
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self): # close connection when done
        self.socket.close()

    def recvall(self, sock): # read everything from the socket
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    # author: Scott Robinson
    # url: https://stackabuse.com/bytes/parsing-urls-with-python/
    # use: how to use the urllib.parse library
    def process_url(self, url): 
        parsed_url = urlparse(url)
        protocol = parsed_url.scheme
        if (protocol != 'http'): # block bad requests
            print("Only http supported.")
            return

        hostname = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        query = parsed_url.query

        if (port is None): # no port provided, use default port
            port = 80
        if (path == ''): # no terminating '/' after hostname; root request
            path = "/"
        if (query): # add query back to path if there is one
            path = path + '?' + query

        return hostname, port, path

    def print_response(self, response): # helper to print server response after GET or POST
        print("==================SERVER RESPONSE START==================")
        print(response)
        print("===================SERVER RESPONSE END===================")

    def GET(self, url, args=None):
        host, port, path = self.process_url(url) # guard against completely wrong and bad host requests?

        self.connect(host, port) # connect to server

        # author: Josh Lee
        # url: https://stackoverflow.com/a/6686276
        # use: how to properly terminate HTTP request with CRLF ending
        request = 'GET %s HTTP/1.1\r\n' % (path) 
        request += 'Host: %s:%s\r\n' % (host, str(port))
        request += 'Connection: Close\r\n\r\n'
        
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()

        response_list = response.split('\r\n') 
        
        self.print_response(response)

        code = self.get_code(response_list[0]) # first element should have status code
        code = int(code) # convert to int
        body = response_list[-1] # last element should be body
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.process_url(url)

        self.connect(host, port) # connect to server

        if (args == None):
            form_data = ''
            size_in_bytes = 0

        else:
            form_data = ''
            for key in args:
                key_value_pair = key + '=' + args[key] + '&'
                form_data +=  key_value_pair

            # author: Goodman
            # url: https://www.slingacademy.com/article/how-to-get-the-size-of-a-string-in-python-in-bytes/
            # use: how to get the byte size of a string
            form_data = form_data[:-1] # delete extra '&' at end
            encoded_bytes = form_data.encode("utf-8")
            size_in_bytes = len(encoded_bytes)

        request = 'POST %s HTTP/1.1\r\n' % (path) 
        request += 'Host: %s:%s\r\n' % (host, port)
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += 'Content-Length: %s\r\n' % (size_in_bytes) 
        request += 'Connection: Close\r\n\r\n'
        request += form_data
        
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()

        response_list = response.split('\r\n')

        self.print_response(response)

        code = self.get_code(response_list[0]) # first element should have status code
        code = int(code) # convert to int
        body = response_list[-1] # last element should be body

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
