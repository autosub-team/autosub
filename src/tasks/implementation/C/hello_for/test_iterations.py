#!/usr/bin/python

import fileinput, optparse, sys

parser = optparse.OptionParser()
parser.add_option("-i", "--iterations", dest="iterations", type="int",
           help=("Number of iterations."))
parser.add_option("-r", action="store_true", dest="reverse", 
           help=("Reverse order"))

parser.set_defaults(iterations=1)
opts, args = parser.parse_args()

if not opts.reverse:
   i = 1
   for line in sys.stdin:
      if (i > opts.iterations):
         print "WRONG: maximum is  " + str(opts.iterations) + "now at:" + str(i)
         print "read: " + line + "."
         sys.exit(1)
      if (line.rstrip() != str(i)):
         print "WRONG: line " + str(i)
         print "read: " + line + "."
         sys.exit(1)
      i+=1

else:
   i = opts.iterations
   for line in sys.stdin:
      if (i <= 0):
         print "WRONG: maximum is  " + str(opts.iterations) + "now at:" + str(i)
         print "read: " + line + "."
         sys.exit(1)
      if (line.rstrip() != str(i)):
         print "WRONG: line " + str(i)
         print "read: " + line + "."
         sys.exit(1)
      i-=1
   
sys.exit(0)
