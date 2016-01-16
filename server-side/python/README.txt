The code in this directory contains python server code to store gps traces:

to run the server simply execute "python track.py". After that you can access the server
using a web brower. As with the original php code no authentication is implemented.

API:
http://localhost:8080/gps?lon=123&lat=123 (optional &t=123)
http://localhost:8080/trace.gpx (to get a gpx trace)
http://localhost:8080/where.html (return the last known posution)


VIEW:
The code also contains a OpenLayers based example that shows the current
location (using /where.html) and the full trace of the user (by fetching
trace.gpx)

The example is based on openlayers version *2* and requires you to download and
install the following Download OpenLayers-2.13 from http://openlayers.org/two/
and after extrating copy (-r) the following files:
- OpenLayers.js  file
- the theme  directory
- the img directry

Afther that you should be able to access the trace by browsing to 
http://localhost:8080/trace.html

DATABASE:
There is a small database (db.sql) being created. If you want to clear the data you can remove it.


PYTHON:
The code is not expected to be secure or stable (My python skills are limited)
