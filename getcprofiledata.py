#!/usr/bin/env python

import sys
import getopt
import os
import time
import urllib, urllib2
import random
import profile
import pstats
import xlsxwriter
import x9
from x9.debug import hack
from x9 import BigWorld
from x9.debug.profile import cProfile


import sys
import getopt

def Usage():
    print 'getcprofile usage:'

    print '-h, --help: show help message.'
    print '-v, --version: show version'
    print '-p, --pattern: input test pattern "5v5"(blown sand ruins),"3v3"(steel mayhem),"FC"(meaning fighting club)'
    print '-d, --duration: input the getting duration,"60"(60 seconds),"1800"(30 minutes),"3600"(1 hour),"0") '
    print '-f, --fps: input the fps when the fps is lower than the value has inputed the data will be stop and start again(find the reasion why lower)'
    print '-s, --span: input the span of data being flushed in to the disk'

def Version():
    print 'getcprofiledata 1.0 '

def main(argv):

    try:
        opts, args = getopt.getopt(argv[1:], 'hvp:d:f:s:', ['help','version','pattern=', 'duration=', 'fps=','span='])

    except getopt.GetoptError, err:
        print str(err)
        print ""
        Usage()
        sys.exit(2)
    if opts == []:
        Usage()
        sys.exit(2)
    pattern,duration,fps,span=None,None,None,None

    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif o in ('-v', '--version'):
            Version()
            sys.exit(0)
        elif o in ('-p', '--pattern'):
            pattern = a
        elif o in ('-d', '--duration'):
            duration = a
        elif o in ('-f', '--fps'):
            fps = a
        elif o in ('-s', '--span'):
            span = a
        else:
            print 'unhandled option'
            sys.exit(3)
    print pattern,duration,fps,span

    isotimeformat='%Y%m%d%H%M%S'
    currenttime = time.strftime(isotimeformat,time.localtime() )
    name = "prof_data_"+pattern+"_"+currenttime
    print name








if __name__ == '__main__':
    main(sys.argv)