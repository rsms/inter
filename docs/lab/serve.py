#!/usr/bin/env python
from __future__ import print_function, absolute_import
import os, sys
import signal
import socket
import http.server
from os.path import dirname, abspath, join as pjoin

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


# make sure "./fonts" is a symlink to /build/fonts
labdir = abspath(dirname(__file__))
try:
  os.symlink('../../build/fonts', pjoin(labdir, 'fonts'))
except OSError:
  pass

addr = ("localhost", 3003)

if len(sys.argv) > 1:
  if sys.argv[1] == '-h':
    print('usage: %s [-h | --bind-any]' % sys.argv[0], file=sys.stdout)
    sys.exit(0)
  elif sys.argv[1] == '--bind-any':
    addr = ("0.0.0.0", 3003)

# make ^C instantly exit program
signal.signal(signal.SIGINT, sighandler)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

httpd = HTTPServer(addr)
print("serving at http://%s:%d/" % addr)
httpd.serve_forever()
