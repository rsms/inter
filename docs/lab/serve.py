#!/usr/bin/env python
from __future__ import print_function, absolute_import
import os, sys
import signal
import SimpleHTTPServer
import socket
import SocketServer

def sighandler(signum, frame):
  sys.stdout.write('\n')
  sys.stdout.flush()
  sys.exit(1)

class TCPServer(SocketServer.TCPServer):
  def server_bind(self):
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind(self.server_address)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# make ^C instantly exit program
signal.signal(signal.SIGINT, sighandler)

httpd = TCPServer(
  ("127.0.0.1", 3002),
  SimpleHTTPServer.SimpleHTTPRequestHandler)

print("serving at http://localhost:3002/")
httpd.serve_forever()
