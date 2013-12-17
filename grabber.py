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
import logging as l
import urllib2
import rfc3987

from bs4 import BeautifulSoup
from reppy.cache import RobotsCache
from time import asctime, gmtime, sleep, strptime, strftime, time

AGENT_DEFAULT = "Paregoricbot/0.1 (+http://www.paregorios.org)"
MAX_SLEEP = 30 # maximum seconds to sleep if directed by robots.txt
OUTFILE_DEFAULT = "placedata.pkl"
PIDFILE_DEFAULT = "places.txt"
PLACES_PATH_DEFAULT = "places"
SCRIPT_DESC = "Grab data from Pleiades using a list of place ids."
SITE_URL_DEFAULT = "http://pleiades.stoa.org"
FORMATS = {
    'xhtml':'/',
    'kml':'/kml',
    'rdf':'/rdf',
    'json':'/json'
}


class PlaceSerialization():
    def __init__(self, parent, format):
        self.format = format
        self.uri = parent.uri + FORMATS[format]
        self.valid = rfc3987.parse(self.uri, rule="absolute_URI")
        if self.valid:
            l.debug("Initialized serialization (%s: %s)." % ((self.format, self.uri)))
        else:
            l.WARNING("%s is not a valid absolute URI, so this serialization will not be retrieved.")

    def fetch(self):
        if self.valid:
            l.debug("Checking robots.txt for access to %s." % self.uri)
            if robots.allowed(self.uri, args.agent):
                self.delay = robots.delay(self.uri, args.agent)
                if self.delay > MAX_SLEEP:
                    l.error("%s was not fetched because robots delay of %s is greater than MAX_SLEEP(%s)" % ((self.delay, MAX_SLEEP, self.uri)))
                elif self.delay > 0:
                    l.debug("Obeying robots.txt directive: sleeping for %s seconds." % self.delay)
                    sleep(self.delay)
                    l.debug("Trying to fetch %s." % self.uri)
                    try: 
                        req = urllib2.Request(self.uri, None, {"user-agent":args.agent})
                        opener = urllib2.build_opener()
                        rsrc = opener.open(req)
                        if self.format == 'json':
                            data = json.load(rsrc)
                            self.datastr = json.dumps(data, ensure_ascii=False)
                            l.debug("JSON retrieved from %s: %s." % (self.uri, self.datastr))
                        elif self.format in ['kml', 'rdf', 'xhtml']:
                            data = BeautifulSoup(rsrc, 'xml')
                            self.datastr = str(data)
                            l.debug("%s retrieved from %s: %s." % (self.format, self.uri, self.datastr))
                        else:
                            l.error("%s is a format that PlaceSerialization.fetch() doesn't know how to retrieve." % self.format)
                        rsrc.close()
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        raise
                else:
                    l.error("%s was not fetched because robots.txt crawl-delay is less than or equal to zero." % s.uri)
            else:
                l.error ("%s was not feteched because robots.txt prohibits access to it." % s.uri)
        else:
            l.error("%s is not a valid absolute URI, and therefore was skipped.")


class Place():
    def __init__(self, pid):
        l.debug("Initializing place with pid=%s." % pid)
        self.pid = pid
        self.uri = "/".join((args.site, args.placepath, pid))
        self.serials = []
        for f in FORMATS.keys():
            if getattr(args, f):
                self.serials.append(PlaceSerialization(self, f))

    def fetchall(self):
        l.debug("Attempting to fetch all requested serializations of place with pid=%s." % self.pid)
        for s in self.serials:
            s.fetch()

    def saveall(self, f):
        l.debug("Attempting to save all requested serializations to output file.")
        x = {
            'pid': self.pid,
            'uri': self.uri
        }
        for s in self.serials:
            x[s.format]=s.datastr

        pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)


def main ():

    global args
    global l
    global robots 
    robots = RobotsCache()
    pidfn = args.pidfile
    outfn = args.outfile

    # open and loop through the contents of the places file
    pf = open(pidfn, "r")
    l.debug("Opened input file '%s' for reading." % pidfn)
    outf = open(outfn, "w")
    l.debug("Opened output file '%s' for writing." % outfn)
    placelist = []
    for (i, line) in enumerate(pf):
        pid = line.rstrip()
        p = Place(pid)
        p.fetchall()
        pd = {}
        pd['pid']=p.pid
        pd['uri']=p.uri
        for s in p.serials:
            pd[s.format]=s.datastr
        placelist.append(pd)
    pickle.dump(placelist, outf, pickle.HIGHEST_PROTOCOL)


    pf.close()
    l.debug("Closed input file '%s'." % pidfn)
    outf.close()
    l.debug("Closed output file '%s'." % outfn)

if __name__ == "__main__":
    try:
        start_time = gmtime()
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
        if args.verbose:
            l.basicConfig(level=l.DEBUG)
        else:
            l.basicConfig(level=l.WARNING)
        l.debug("Started at %s." % asctime(start_time))
        main()
        end_time = gmtime()
        l.debug("Finished at %s. Total time in minutes: %s" % asctime(end_time))
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
