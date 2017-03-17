#!/usr/bin/python3
import os,sys
import cgi
import cgitb; cgitb.enable()

# set HOME environment variable to a directory the httpd server can write to
os.environ[ 'HOME' ] = '/tmp/'

import matplotlib
# chose a non-GUI backend
matplotlib.use( 'Agg' )

import pylab

#Deals with inputing data into python from the html form
form = cgi.FieldStorage()

# construct your plot
pylab.plot([1,2,3])

sys.stdout.buffer.write (b"Content-Type: image/png\r\n\r\n")

#print(b"\r\n")
# save the plot as a png and output directly to webserver
pylab.savefig( sys.stdout.buffer, format='png' )

#pylab.savefig( "tempfile.png", format='png' )

