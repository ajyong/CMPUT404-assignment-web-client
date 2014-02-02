#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Aaron Yong
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
import urllib
# parsing input URL to get host and port
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # request parsing functions
    def get_port(self,url):
        if url is not None:
            colon_pos = -1
            if url.startswith("http://"):
                colon_pos = url.find(":", 7)
            else:
                colon_pos = url.find(":")

            if colon_pos == -1:
                return "80"

            path_pos = url.find("/", colon_pos)
            if path_pos == -1:
                return url[colon_pos + 1:]
            else:
                return url[colon_pos + 1:path_pos]
        else:
            return None

    def get_host(self, url):
        if url is not None:
            if url.startswith("http://"):
                colon_pos = url.find(":", 7)
                path_pos = url.find("/", 7)

                if colon_pos != -1:
                    # if port specified, return string between http:// and :PORT
                    return url[7:colon_pos]
                elif path_pos != -1:
                    # if no port but added paths, return part without http:// and without added paths
                    return url[7:path_pos]
                else:
                    # if no port or added paths, return part of the URL without http://
                    return url[7:]
            else:
                # doesn't start with http://
                colon_pos = url.find(":")
                path_pos = url.find("/")

                if colon_pos != -1:
                    # if port specified, return string between http:// and :PORT
                    return url[:colon_pos]
                elif path_pos != -1:
                    # if no port but added paths, return part without http:// and without added paths
                    return url[:path_pos]
                else:
                    # if no port or added paths, return the URL
                    return url
        else:
            return None

    def get_path(self,url):
        if url is not None:
            slash_pos = -1
            if url.startswith("http://"):
                slash_pos = url.find("/", 7)
            else:
                slash_pos = url.find("/")

            if slash_pos == -1:
                return "/"
            else:
                return url[slash_pos:]
        else:
            return None

    def connect(self, host, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            return s
        except Exception as e:
            print e
            return None

    # response parsing functions
    def get_code(self, data):
        return int(data[9:12])

    def get_headers(self, data):
        return None

    def get_body(self, data):
        lines = data.splitlines(True)
        blank_line_pos = -1

        for i in range(len(lines)):
            if lines[i] == "\r\n" or lines[i] == "\n" or lines[i] == "\r":
                blank_line_pos = i
                break

        body = ""
        for j in range(i, len(lines)):
            body += lines[j]

        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        host = self.get_host(url)
        port = self.get_port(url)
        path = self.get_path(url)

        sock = self.connect(host, port)
        if sock != None:
            request = "GET %s HTTP/1.1\r\n" \
                      "Host: %s\r\n" \
                      "Connection: close\r\n" \
                      "Accept: */*\r\n\r\n" % (path, host)

            try:
                sock.send(request)
            except Exception as e:
                print e
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

                return HTTPRequest(code, body)

            data = self.recvall(sock)

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

            code = self.get_code(data)
            body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host = self.get_host(url)
        port = self.get_port(url)
        path = self.get_path(url)

        sock = self.connect(host, port)
        if sock != None:
            request = "POST %s HTTP/1.1\r\n" \
                      "Host: %s\r\n" \
                      "Connection: close\r\n" \
                      "Content-Type: application/x-www-form-urlencoded\r\n" \
                      "Accept: */*\r\n" % (path, host)

            if args != None:
                form_data = urllib.urlencode(args)
                request += "Content-Length: %d\r\n" \
                           "\r\n" \
                           "%s\r\n" % (len(form_data), form_data)
            else:
                request += "Content-Length: 0\r\n\r\n"

            try:
                sock.send(request)
            except Exception as e:
                print e
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

                return HTTPRequest(code, body)

            data = self.recvall(sock)

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

            code = self.get_code(data)
            body = self.get_body(data)

        return HTTPRequest(code, body)

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
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1], command )    
