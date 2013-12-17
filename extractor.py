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
import json
import logging as l

from bs4 import BeautifulSoup
from time import strptime

SCRIPT_DESC = "Organize and mine previously grabbed data from Pleiades."
PICKLEFILE_DEFAULT = "pdata.pkl"
FORMATS = {
    'xhtml':'',
    'kml':'/kml',
    'rdf':'/rdf',
    'json':'/json'
}




def main ():

    global args
    global l

    pfn = args.picklefile

    # open and loop through the contents of the places file
    pf = open(pfn, "rb")
    l.debug("Opened input file '%s' for reading." % pfn)
    dlist = pickle.load(pf)
    pf.close()
    l.debug("Closed input file '%s'." % pfn)

    plist = []
    for d in dlist:
        j = k = r = x = False
        p = {}
        if 'json' in d.keys():
            j = True
            dj = json.loads(d['json'])
        if 'kml' in d.keys():
            k = True
            dk = BeautifulSoup(d['kml'], 'lxml')
        if 'rdf' in d.keys():
            r = True
            dr = BeautifulSoup(d['rdf'], 'lxml')
        if 'xhtml' in d.keys():
            x = True
            dx = BeautifulSoup(d['xhtml'], 'lxml')
        # title
        if j:
            p['title']=dj['title']
        else:
            pass
        # description
        if j:
            p['description']=dj['description']
        else:
            pass
        # last modification
        if x:
            lastmod = dx.find_all("div", class_='historyByLine')[0]
            p['modifier']=lastmod.a.string
            p['modification']=lastmod.parent.find("div", class_='historyComment').string
            modstring = ' '.join(lastmod.a.next_sibling.split()).replace('on ', '')
            print "modstring: %s" % modstring
            moddate = strptime(modstring, "%b %d, %Y %I:%M %p")
            p['moddate']=moddate


        print p

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description=SCRIPT_DESC, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument ("picklefile", default=PICKLEFILE_DEFAULT, 
            help="text file containing list of Pleiades IDs (short, numeric form, not URIs)")
        parser.add_argument ("-v", "--verbose", action="store_true", default=False, help="verbose output")
        args = parser.parse_args()
        if args.verbose:
            l.basicConfig(level=l.DEBUG)
        else:
            l.basicConfig(level=l.WARNING)
        main()
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
