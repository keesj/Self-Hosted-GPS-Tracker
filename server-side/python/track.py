#!/usr/bin/env python
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs

import datetime
import time

import sqlite3
import time

import StringIO

ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"

#
# Open and possibly create a database where we can store gps traces
# The database is designed to support multiple traces
#
db = sqlite3.connect('db.sql',detect_types=sqlite3.PARSE_DECLTYPES)
db.execute("CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY,device_id INTEGER, ts INTEGER , long READ, lat REAL,props TEXT)")

count=0

class TrackHandler(SimpleHTTPRequestHandler):

	def __init__(self,request, client_address, server):
		SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

	def do_msg(self,message,code):
		self.send_response(code)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-length", len(message))
		self.end_headers()
		print (message)
		self.wfile.write(message)

	def do_err(self,message):
		self.do_msg(message,500)

	def do_ok(self,message):
		self.do_msg(message,200)

	def do_handle_pos(self,device_id):
		global count
		q = parse_qs(urlparse(self.path).query)

		if q.has_key('tracker'):
			print("tracker start/stop")
			self.do_ok("tracker start/top")
			return

		if not q.has_key('lon'):
			self.do_err("Missing lon")
			return

		if not q.has_key('lat'):
			self.do_err("Missing lat")
			return

		#python skills lacking here I think this might crash the server if given wrong
		#parameters
		lon = float(q["lon"][0])
		lat = float(q["lat"][0])


		t = time.mktime(time.localtime())
		if q.has_key('t'):
			t = time.mktime(time.localtime(float(q['t'][0])/1000))

		#
		# do a query to see if an entry with that timestamp already exists
		#
		x =  db.execute("SELECT COUNT(*) from locations where ts = ? and device_id = ?" , [t,device_id])
		value = x.fetchone()[0]
		text = "OK"
		if value == 0:
			#
			# Insert a point into the database
			#
			count = count +1
			db.execute("INSERT into locations(device_id,ts,long,lat) values(?,?,?,?)",(device_id,t,repr (lon),repr( lat)))
			if (count % 100 == 0):
				db.commit()
			self.do_ok("OK");
		else:
			#
			# skip we already got an entry
			#
			self.do_ok("OK DUP")

	def do_handle_trace(self,device_id):
		#
		# Generate a gpx trace for the given ID
		#
		output = StringIO.StringIO()

		for row in db.execute('SELECT id,ts,long,lat FROM locations WHERE device_id = ? ORDER BY ts desc limit 1',[device_id]):
			t = time.localtime(row[1])
        		output.write ("%s_%s_%s_\n" %(time.strftime("%Y-%m-%d %H:%M:%S",t), row[3],row[2]))

		content = output.getvalue()
		self.send_response(200)
		self.send_header("Content-type", "application/gpx+xml")
		self.send_header("Content-length", len(content))
		self.end_headers()
		self.wfile.write(content)

	def do_handle_track(self,device_id):
		output = StringIO.StringIO()


       		output.write ("<gpx>\n")
       		output.write (" <trk>\n")
       		output.write ("  <name>GPX trace</name>\n")
       		output.write ("  <trkseg>\n")
		for row in db.execute('SELECT id,ts,long,lat FROM locations WHERE device_id = ? ORDER BY ts asc',[device_id]):
			t = time.localtime(row[1])
        		output.write ("    <trkpt lat=\"%s\" lon=\"%s\">\n" %(row[3],row[2]))
        		output.write ("     <time>%s</time>\n" %(time.strftime("%Y-%m-%d %H:%M:%S",t)))
        		output.write ("    </trkpt>\n")
       		output.write ("  </trkseg>\n")
       		output.write (" </trk>\n")
       		output.write ("</gpx>\n")

		content = output.getvalue()
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-length", len(content))
		self.end_headers()
		self.wfile.write(content)

	def do_OPTIONS(self):
		#
		# Allo other sites to make to cross site requests (e.g. include a map
		# on a different site.
		#
		self.send_response(200, "ok")
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "X-Requested-With")

	def do_GET(self):
		print (self.path);

		#
		# handle the original /gps entry (assumes device id is 1...)
		# TODO:
		# -Use some form of authentication. For the Android app
  		# it would be very nice to sign and encrypt the data:
		# 
		# on Application startup the app should generate a keypair and upload
		# the public key to this server. Next it should sign the requests to this
		# service.
		#
		# At the same time the access to "/trace.gpx" should be guarded by an app key
		# e.g. this python server side code should keep a mapping of key->device id
		# for example /trace.gpx?key=123234 should be mapped to device id 1
		#
		if self.path.startswith("/gps"):
			self.do_handle_pos(1)
			return

		if self.path.startswith("/where.html"):
			self.do_handle_trace(1)
			return

		if self.path.startswith("/trace.gpx"):
			self.do_handle_track(1)
			return

		if self.path in ("/trace.html", "/OpenLayers.js"):
			return  SimpleHTTPRequestHandler.do_GET(self)

		if self.path.startswith("/theme"):
			return  SimpleHTTPRequestHandler.do_GET(self)
		if self.path.startswith("/img"):
			return  SimpleHTTPRequestHandler.do_GET(self)

		self.do_ok("NOTHING TO SEE HERE")


HandlerClass = TrackHandler

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080
server_address = ('0.0.0.0', port)

HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
try:
	httpd.serve_forever()
except:
	print "Commiting db"
	db.commit()
