#!/usr/bin/python3
import os,sys
import cgi
import cgitb; cgitb.enable()
import shutil
import io
from io import BytesIO

# set HOME environment variable to a directory the httpd server can write to
os.environ[ 'HOME' ] = '/tmp/'

import matplotlib
# chose a non-GUI backend
matplotlib.use( 'Agg' )

import pylab
import snc_tools3
import numpy
#import argparse

#parser = argparse.ArgumentParser()
#args = parser.parse_args()
#print(args)

#Deals with inputing data into python from the html form
form = cgi.FieldStorage()

#print (os.environ[ "QUERY_STRING"])
#params={"template":"","filter":"","magnitude":"","sens_func":"","exptime":1,"slit":"","seeing":"","fwhm":"","extinction_curve":"","airmass":1}
params={"magnitude":"","template":"","filter":""}
templ_dic={"Elliptical Galaxy":"data/eGalaxy_ang.dat","Sc Galaxy":"data/scGalaxy_ang.dat","star A0":"data/A0V.dat"}
disperser_dic={"IMACS-grism_200":"Grism200.dat","IMACS-grism300b":"Grism300B.dat",
               "IMACS grism 300R":"Grism300R.dat",
               "MAGE":"mage.dat",
               "Mike-Blue":"mikeb.dat",
               "Mike-Red":"miker.dat"}
filter_dic={"V":"data/bess-v.pass","R":"data/bess-r.pass","U":"data/bess-u.pass","B":"data/bess-b.pass","I":"data/bess-i.pass"}

if 'magnitude' in form:
#if form.has_key("magnitude"):
    magnitude=form.getvalue("magnitude")

else:
    magnitude=0
m=float(magnitude)

templatefile=templ_dic[form.getvalue("template")]
filterfile=filter_dic[form.getvalue("filter")]
sfilterfile=filter_dic[form.getvalue("sfilter")]

obj=snc_tools3.FluxTools(template=templatefile,magnitude=m,filter=filterfile)

######################
## This needs to be here first.
#print ("Content-Type: text/html")     # Just set the standard html content type.
#print                               # Blank line signifies the end of the header info.
#
#print ("<title>MAGELLAN ETC</title>")
#print ("<body>")
#print ("<h1> MAGELLAN EXPOSURE TIME CALCULATOR </h1>")
#print ("<h1> %s %s</h1>" % (filterfile,templatefile))
obj_ab=obj.ToABmag(m)
sens=numpy.genfromtxt("data/"+disperser_dic[form.getvalue("disperser")])[:,0:2]
ctio=numpy.genfromtxt("data/ctioextinct.dat")
airmass=float(form.getvalue("airmass"))
expt=float(form.getvalue("exptime"))
seeing=float(form.getvalue("seeing"))

#fw=float(form.getvalue("fwhm"))

slit=float(form.getvalue("slit"))
magsky=float(form.getvalue("magsky"))
counts=snc_tools3.SignalTools(object=obj_ab,sens_func=sens,exptime=expt,airmass=airmass,slit=slit,extinction_curve=ctio,fwhm=seeing,seeing=seeing)
counts_spectrum=counts.GetCounts()
#add slit losses
losses=counts.slit_tran()
counts_spectrum[:,1]=counts_spectrum[:,1]*losses
sky=snc_tools3.FluxTools(template="data/UVES_sky_smo.txt",filter="data/filterV_ang.dat",magnitude=magsky)
sm=sky.SedToMag(const=1)
sky_ab=sky.ToABmag(magsky)
#counts.airmass=1
#counts.object=sky_ab
#skycounts=counts.GetCounts()
skyc=snc_tools3.SignalTools(object=sky_ab,sens_func=sens,exptime=expt,airmass=1.,slit=slit,extinction_curve=ctio,fwhm=seeing,seeing=seeing)
skycounts=skyc.GetCounts()
spatscale=0.2
specscale=1.2

skycounts[:,1]=(skycounts[:,1])*seeing*slit

# construct your plot
##pylab.plot(obj_ab[:,0],obj_ab[:,1])
#pylab.plot([1,2,3])
pylab.plot(counts_spectrum[:,0],counts_spectrum[:,1])
pylab.plot(skycounts[:,0],skycounts[:,1])
##pylab.plot(sky_ab[:,0],sky_ab[:,1])
pylab.title("disperser=%s obj mag.=%s exptime=%s" % (form.getvalue("disperser"),form.getvalue("magnitude"),form.getvalue("exptime") ))
pylab.xlabel("Wavelength",size=15)
pylab.ylabel("Counts/Angstrom",size=15)
pylab.legend(("object","sky"))

#New type of print statement needed
#-------------------------------------
#print=sys.stdout.buffer.write
#print ("Content-Type: image/png\n")
#pylab.savefig( sys.stdout, format='png' )
sys.stdout.buffer.write (b"Content-Type: image/png\r\n\r\n")


# save the plot as a png and output directly to webserver
pylab.savefig( sys.stdout.buffer, format='png' )
#pylab.show()
#pylab.savefig("tempfile.png", format='png')
#figdata.seek(0)
#shutil.copyfileobj(figdata, sys.stdout.buffer)

