#!/usr/bin/env python

# This script replaces all blank nodes with named nodes by skolemizing [1] the input file. It will
# create a new bnode: namespace where the new named nodes are definde.
#
# [1] http://answers.semanticweb.com/questions/8336/what-is-skolemization
#
# Usage:
#   -i --input=     The input file
#   -o --output=    The output file (optional)
#   -h --help       Usage information
#
# Requirements:
#   Redland librdf python interface <http://librdf.org/docs/python.html>
#   Debian users cann install these bindings with "apt-get install python-librdf"
#
# Copyright:    (c) 2013 AKSW <http://aksw.org/>
# License:      GNU General Public License (GPL) <http://opensource.org/licenses/gpl-license.php>
# Author:       Natanael Arndt <http://aksw.org/NatanaelArndt>

import sys
import getopt
import re
import RDF

args, opts = getopt.getopt(sys.argv[1:], "i:o:h", ["input=", "output=", "help"])

def help():
    sys.stderr.write("""
Usage:
  -i --input=     The input file
  -o --output=    The output file (optional)
  -h --help       Usage information

""")

outputUri = None
inputUri = None
for opt, arg in args:
    if opt in ("-i", "--input"):
        inputUri = "file:" + arg
    elif opt in ("-o", "--output"):
        outputUri = arg
    elif opt in ("-h", "--help"):
        help()
        sys.exit(0)

if (inputUri == None) :
    sys.stderr.write("\nNo input file given.\n")
    help()
    sys.exit(1)

sys.stderr.write("Input: " + inputUri + "\n")

ttlParser = RDF.TurtleParser()
inStream = ttlParser.parse_as_stream(inputUri)
namespaces = ttlParser.namespaces_seen()

ntrSerializer = RDF.NTriplesSerializer()

string = ntrSerializer.serialize_stream_to_string(inStream)

bnode = re.compile(r'_(:[r0-9]+)')
string = re.sub(bnode, r'<bnode\1>', string)

outStream = ttlParser.parse_string_as_stream(string, inputUri)

ttlSerializer = RDF.Serializer(name="turtle")
ttlSerializer.set_namespace("bnode", "http://example.com/bnode/")
for prefix, uri in namespaces.iteritems():
    ttlSerializer.set_namespace(prefix, uri)

string = ttlSerializer.serialize_stream_to_string(outStream)

if (outputUri):
    outFile = open(outputUri, "w")
else:
    outFile = sys.stdout
outFile.write(string)
sys.stderr.write("done\n")
