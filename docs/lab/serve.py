#!/usr/bin/env python
from __future__ import print_function, absolute_import
import os, sys
import signal
import socket
import http.server

def sighandler(signum, frame):
  sys.stdout.write('\n')
  sys.stdout.flush()
  sys.exit(1)


class HTTPServer(http.server.HTTPServer):
  def __init__(self, addr):
    http.server.HTTPServer.__init__(
      self, addr, http.server.SimpleHTTPRequestHandler)

  def server_bind(self):
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    http.server.HTTPServer.server_bind(self)


addr = ("localhost", 3002)

# make ^C instantly exit program
signal.signal(signal.SIGINT, sighandler)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

httpd = HTTPServer(addr)
print("serving at http://%s:%d/" % addr)
httpd.serve_forever()
