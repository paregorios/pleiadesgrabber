#!/usr/bin/env python
"""
SYNOPSIS

    TODO grabber [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    TODO: Show some examples of how to use this script.

EXIT STATUS

    TODO: List exit codes

AUTHOR

    TODO: Name <name@example.org>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.

VERSION

    $Id$
"""

import sys, os, traceback, argparse
import pickle
import re
import json
import urllib2

from reppy.cache import RobotsCache
from time import asctime, sleep, strptime, strftime, time

AGENT_DEFAULT = "Paregoricbot/0.1 (+http://www.paregorios.org)"
MAX_SLEEP = 30 # maximum seconds to sleep if directed by robots.txt
OUTFILE_DEFAULT = "placedata.pkl"
PIDFILE_DEFAULT = "places.txt"
PLACES_PATH_DEFAULT = "places"
SCRIPT_DESC = "Grab data from Pleiades using a list of place ids."
SITE_URL_DEFAULT = "http://pleiades.stoa.org"
FORMATS = {
    'xhtml':'',
    'kml':'/kml',
    'rdf':'/rdf',
    'json':'/json'
}

def formatExceptionInfo(maxTBlevel=5):
     cla, exc, trbk = sys.exc_info()
     excName = cla.__name__
     try:
         excArgs = exc.__dict__["args"]
     except KeyError:
         excArgs = "<no args>"
     excTb = traceback.format_tb(trbk, maxTBlevel)
     return (excName, excArgs, excTb)

def jout(j):
    lastmods = j['recent_changes'][0]['modified']
    lastmoddt = strptime(lastmods)
    lastmodd = strftime(lastmoddt, '%X')
    lastmodt = strftime(lastmoddt, '%x')
    if args.verbose:
        print "lastmods: %s" % lastmods
        print "lastmodd: %s" % lastmodd
        print "lastmodt: %s" % lastmodt
    lastmodpers = j['recent_changes'][0]['principal']
    z = '<li>\n' \
        + '    <a href="http://pleiades.stoa.org/%s">%s</a>: %s (last modified at %s on %s by %s)\n' \
            % (j['id'], j['title'], j['description'], lastmodt, lastmodd, lastmodpers) \
        + '</li>\n'

    print z

class PlaceSerialization():
    def __init__(self, parent, format):
        self.format = format
        self.uri = parent.uri + FORMATS[format]
        if args.verbose: print "Initialized serialization (%s: %s)." % ((self.format, self.uri))

class Place():
    def __init__(self, pid):
        if args.verbose: print "Initializing place with pid=%s." % pid
        self.pid = pid
        self.uri = "/".join((args.site, args.placepath, pid))
        self.serials = []
        for f in FORMATS.keys():
            if getattr(args, f):
                self.serials.append(PlaceSerialization(self, f))

    def fetchall(self):
        if args.verbose: print "Attempting to fetch all requested serializations of place with pid=%s." % self.pid
        for s in self.serials:
            if robots.allowed(s.uri, args.agent):
                s = robots.delay(s.uri, args.agent)
                if s > MAX_SLEEP:
                    print "NOFETCH >>> robots delay of %s is greater than MAX_SLEEP(%s): %s" % ((s, MAX_SLEEP, s.uri))
                elif s > 0:
                    if args.verbose: print "Obeying robots.txt directive: sleeping for %s seconds." % s
                    sleep(s)
                    if args.verbose: "%s is allowed. Trying..." % url
                        try: 
                            req = urllib2.Request(url, None, {"user-agent":args.agent})
                            opener = urllib2.build_opener()
                            rsrc = opener.open(req)
                            if s.format = 'json':
                                self.data = json.load(rsrc)
                            elif s.format = 'xhtml':
                                soup = BeautifulSoup(rsrc, 'xml')
                            elif s.format = 'rdf':
                                pass
                            elif s.format = 'kml':
                                pass
                            else:
                                print "UNKOWNFORMAT"
                            
                p.close()
            except:
                print formatExceptionInfo()
            if args.verbose: print pjson
            pickle.dump(pjson, outf, pickle.HIGHEST_PROTOCOL)
                else:
                    print "NOFETCH >>> robots delay is less than or equal to zero: %s" % s.uri  
            else:
                print "NOFETCH >>> robots.txt prohibits access to %s." % s.uri



def main ():

    global args
    global robots 
    robots = RobotsCache()
    pidfn = args.pidfile
    outfn = args.outfile
    # test URLs?


    # open and loop through the contents of the places file
    pf = open(pidfn, "r")
    if args.verbose: print "Opened input file '%s' for reading." % pidfn
    outf = open(outfn, "w")
    if args.verbose: print "Opened output file '%s' for writing." % outfn
    for (i, line) in enumerate(pf):
        pid = line.rstrip()
        p = Place(pid)
        p.fetchall()

#        if args.verbose: print "sleeping for %s seconds" % delay
#        sleep(delay)
#        url = "%s/%s/json" % (placebase, pid)
#        if robots.allowed(url, agent):
#            if args.verbose: "%s is allowed. Trying..." % url
#            try: 
#                req = urllib2.Request(url, None, {"user-agent":agent})
#                opener = urllib2.build_opener()
#                p = opener.open(req)
#                pjson = json.load(p)
#                p.close()
#            except:
#                print formatExceptionInfo()
#            if args.verbose: print pjson
#            pickle.dump(pjson, outf, pickle.HIGHEST_PROTOCOL)
#        else:
#            print "DENIED by robots.txt: %s" % url
    pf.close()
    outf.close()

if __name__ == "__main__":
    try:
        start_time = time()
        parser = argparse.ArgumentParser(description=SCRIPT_DESC, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument ("pidfile", default=PIDFILE_DEFAULT, 
            help="text file containing list of Pleiades IDs (short, numeric form, not URIs)")
        parser.add_argument ("outfile", default=OUTFILE_DEFAULT,
            help="output file for pickled data")
        parser.add_argument ("-a", "--agent", default=AGENT_DEFAULT, help="set user agent string to be used in HTTP requests")
        parser.add_argument ("-x", "--xhtml", action="store_true", default=False, help="capture XHTML representation")
        parser.add_argument ("-j", "--json", action="store_true", default=False, help="capture JSON representation")
        parser.add_argument ("-k", "--kml", action="store_true", default=False, help="capture KML representation")
        parser.add_argument ("-p", "--placepath", default=PLACES_PATH_DEFAULT, help="override the default places URL path")
        parser.add_argument ("-r", "--rdf", action="store_true", default=False, help="capture RDF representation")
        parser.add_argument ("-s", "--site", default=SITE_URL_DEFAULT, help="override the default site URL")
        parser.add_argument ("-v", "--verbose", action="store_true", default=False, help="verbose output")
        args = parser.parse_args()
        if not(args.xhtml) and not(args.json) and not(args.kml) and not(args.rdf):
            parser.error ("No grabbable format specified; nothing will be retrieved. Try using -h option for more help.")
        if args.verbose: print asctime()
        main()
        if args.verbose: print asctime()
        if args.verbose: print "TOTAL TIME IN MINUTES:",
        if args.verbose: print (time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        os._exit(1)
