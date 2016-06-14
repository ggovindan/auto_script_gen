#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import simplejson
import random
import read_json
import sys
import traceback
 
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
 
    def do_GET(self):
        print "self.path=", self.path
        if self.path == "/":
            self._set_headers()
            f = open("index.html", "r")
            self.wfile.write(f.read())
        elif self.path == "/help":
            self._set_headers()
            f = open("help.html", "r")
            self.wfile.write(f.read())
 
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        print "in post method"
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        print "data_string: ", self.data_string
        try:
            data = simplejson.loads(self.data_string)
            with open("test7777777.json", "w") as outfile:
                simplejson.dump(data, outfile)
                
            read_json.main("test7777777.json", None)
            f = open("test7777777.py", "r")
            self._set_headers()
            self.wfile.write(f.read())
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print ''.join('! ' + line for line in lines)            
            mystr = ''.join('! ' + line for line in lines)
            self.send_header('Content-type', 'text')
            self.wfile.write(mystr)

        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()
 
if __name__ == "__main__":
    from sys import argv
 
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
