#!/usr/bin/python3

#switch to python3
###/Applications/scisoft/i386/bin/python2.5
#on the previous line I had to hard code the path to my python binary to find the additional modules pylab,scipy etc.


# For CGI support 
import cgi
# For debugging support
import cgitb; cgitb.enable()
import argparse
# import needed libraries:
import os,sys
#os.environ[ 'HOME' ] = '/var/tmp' # point to a writable tmp dir 
#import matplotlib
# chose a non-GUI backend
#matplotlib.use( 'Agg' )

#import snc_tools
#import pylab
#import numpy


#os.system('export QUERY_STRING=""')


templ_dic={"Elliptical Galaxy":"Ell.dat","Sc Galaxy":"sc.dat","star A0":"AO.dat"}
disperser_dic={"IMACS-grism_200":"grism200.dat","IMACS-grism300b":"grism300B.dat",
               "IMACS grism 300R":"grism300R.dat",
               "MAGE":"mage.dat",
               "Mike-Blue":"mikeb.dat",
               "Mike-Red":"miker.dat"}
#filter_dic={"V":"filte_V.dat","R":"R_filte.dat"}
filter_dic={"V":"data/bess-v.pass","R":"data/bess-r.pass","U":"data/bess-u.pass","B":"data/bess-b.pass","I":"data/bess-i.pass"}

sfilter_dic={"V":"data/bess-v.pass"}


def MakeOptionList(keyword,list):
    selected=form.getvalue(keyword)
    print ("<SELECT NAME=%s >" % (keyword))
    for item in list:
        if item==selected:
            print ("<OPTION %s selected> %s </OPTION>" % (item,item))
        else:
            
            print ("<OPTION %s> %s </OPTION>" % (item,item))
            
    print ("</SELECT>")
def MakeInputBox(keyword):
    print ("<INPUT TYPE=TEXT NAME=%s SIZE=5 MAXLENGTH=4 value=%s>" % (keyword,form.getvalue(keyword)))
    

# This needs to be here first.
print ("Content-Type: text/html")     # Just set the standard html content type.
print  ()                             # Blank line signifies the end of the header info.

print ("<title>MAGELLAN ETC</title>")
print ("<body>")
print ("<h1> MAGELLAN EXPOSURE TIME CALCULATOR </h1>")


form = cgi.FieldStorage()

#if form.has_key('template'):
if 'template' in form:
    template=form.getvalue("template")
else:
    template="bo"

#if form.has_key('disperser'):
if 'disperser' in form:
    disperser=form.getvalue("disperser")
else:
    disperser="IMACS grism_200"

#if form.has_key("magnitude"):
if "magnitude" in form:
    magnitude=form.getvalue("magnitude")
else:
    magnitude=15

#if form.has_key("filter"):
if "filter" in form:
    filter=form.getvalue("filter")
else:
    filter="V"
#if form.has_key("sfilter"):
if "sfilter" in form:
    sfilter=form.getvalue("sfilter")
else:
    sfilter="V"
#if form.has_key("slit"):
if "slit" in form:
    slit=form.getvalue("slit")
else:
    slit=1

#if form.has_key("seeing"):
if "seeing" in form:
    seeing=form.getvalue("seeing")
else:
    seeing=1

#if form.has_key("magsky"):
if "magsky" in form:
    smagnitude=form.getvalue("magsky")
else:
    smagnitude=21.8

#--------------------------------------
#NEW="print("smagnitude=",smagnitude,"&seeing=",seeing,slit,sfilter,...)
#--------------------------------------
print ('<FORM action="magellan_etc3.py" method="GET" enctype="application/x-www-form-urlencoded">')
print ("<b>")

print ("<fieldset>")
print ("<legend>Target</legend>")
print ("Template")
MakeOptionList("template",templ_dic.keys())

#
print ("Magnitude:<INPUT TYPE=TEXT NAME=magnitude SIZE=5 MAXLENGTH=4 value=%s>" % str(magnitude))

MakeOptionList("filter",["B","V","R","I"])

print ("</fieldset>")





print ("<fieldset>")
print ("<legend>Instrument Setup</legend>")
print ("Disperser")
MakeOptionList("disperser",disperser_dic.keys())

print ("SLIT <INPUT TYPE=TEXT NAME=slit value=%s SIZE=3 MAXLENGTH=3> arcsec" % str(slit))
print ("</fieldset>")

print ("<fieldset>")
print ("<legend>Observing Conditions</legend>")

print (" SEEING (arcsec)")
MakeInputBox("seeing")

print ("AIRMASS <INPUT TYPE=TEXT NAME=airmass value=1 SIZE=3 MAXLENGTH=3>")
print ("<BR><BR>")

print ("Sky Brightness (mag/arcsec^2) <INPUT TYPE=TEXT NAME=magsky value=%s SIZE=4 MAXLENGTH=4>" % str(smagnitude))
print ("Band")

MakeOptionList("sfilter",sfilter_dic)


print ("</fieldset>")

print ("<fieldset>")
print ("<legend>CCD Setup</legend>")
#print "Exptime (seconds)<INPUT TYPE=TEXT NAME=exptime value=1 SIZE=4 MAXLENGTH=4>"
print ("Exptime (seconds)")
MakeInputBox("exptime")

print ("</fieldset>")



print ('<br><INPUT type="submit" value="CALCULATE">')


#do a get on all values and generate all query string?
#-------------------------------
TEST_STRING="template=Sc+Galaxy&magnitude=15&filter=B&disperser=IMACS+grism+300R&slit=1&seeing=None&airmass=1&magsky=21.8&sfilter=V&exptime=12"
#---------------------------------

#
#if form.has_key("template"):
#        template=form.getvalue("template")
#        print "<h2> the template is %s with file %s </h2>" % (template,templ_dic[template])
#        
#
#if form.has_key('magnitude'):
#    
#    magnitude =float(form.getvalue('magnitude'))
#    
#    
#    print "<h2> the magnitude is %s </h2>" % str(magnitude)
#
#    
#
#if form.has_key("filter"):
#        filter=form.getvalue("filter")
#        print "<h2> the filter is %s </h2>" % filter
#if form.has_key("SFILTER"):
#    sfilter=form.getvalue("SFILTER")
#    print "<h2> the sky filter is %s </h2>" % sfilter
#else:
#    pass
#if form.has_key("disperser"):
#    disperser=form.getvalue("disperser")
#    print "<h2> the disperser is %s and file %s</h2>" % (disperser,disperser_dic[disperser])
#print (os.environ[ "QUERY_STRING" ])
#-----------------------
#This is the one we were using below
print ("<center><img src=image3.py?%s></center>" % (os.environ[ "QUERY_STRING" ]))
#----------------------
#new try at passing information with the POST method
#print ("<center><img src=image3.py?%s></center>" % (TEST_STRING))
#----------------------
#print "<div>"
#print    """<table width="100%" height="100%" align="center" valign="center">"""
#print    "<tr><td>"
#print  "<img src=image.py?%s alt=foo />" % (os.environ[ "QUERY_STRING" ])
#print    "</td></tr>"
#print   "</table>"
#print "</div>"

print ("</b>")
print ("</FORM>")

#print (os.environ["QUERY_STRING"])

#for param in os.environ.keys():
#  print ("<b>%20s</b>: %s<\br>" % (param, os.environ[param]))
