#!/usr/bin/env python
# For systems with python 2 as standard, change above line to ...python3

import rdflib
import sys
import argparse
import yaml
import re
import io
parser = argparse.ArgumentParser()

parser.add_argument("mode", choices=['ow2git', 'git2ow'])
parser.add_argument("file")
parser.add_argument("-i", "--input", default="turtle", help="Input format")
parser.add_argument("-o", "--output", default="turtle", help="Output format")
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")

# reading parameters
args = parser.parse_args()

# reading config file
configFile = open("git2ow.yml", 'r')
_config = yaml.load(configFile)

def bindPrefixes(g):
    """
    Binds prefixes in a graph that are used for serialization. The function
    modifies the graph in-place

    arguments:
    g -- an rdflib.Graph
    """
    for prefix, namespace in _config['prefixes'].items():
        g.bind(prefix, namespace)


def getOwlCollections():
    getCollections = """SELECT ?collClass WHERE {
       ?collClass owl:oneOf ?coll .
    }"""
    return getCollections


def getDesignatorInsert(col):
    insertDesignator = """INSERT {{
        <{0}> <%s> "%s" .
    }}
    WHERE {{ }} """ % (
        _config['dropdownDesignator']['property'],
        _config['dropdownDesignator']['value']
    )
    return insertDesignator.format(col);


def getOrderInsert(col):
    insertCounts = """INSERT {{
        ?elem <%s> ?pos .
        ?elem a <{0}> .
    }}
    WHERE {{
        SELECT ?elem (COUNT(?mid) AS ?pos)
        WHERE {{
            <{0}> <http://www.w3.org/2002/07/owl#oneOf> ?coll .
            ?coll rdf:rest* ?mid .
            ?mid rdf:rest* ?bnode .
            ?bnode rdf:first ?elem .
        }} GROUP BY ?bnode ?elem
    }}""" % _config['orderProperty']
    return insertCounts.format(col)


def getCollectionDelete(col):
    deleteCollection = """DELETE {{
        <{0}> <http://www.w3.org/2002/07/owl#oneOf> ?coll .
        ?bnode rdf:first ?elem .
        ?bnode rdf:rest ?rest .
    }}
    WHERE {{
        <{0}> <http://www.w3.org/2002/07/owl#oneOf> ?coll .
        ?coll rdf:rest* ?bnode .
        ?bnode rdf:first ?elem .
        ?bnode rdf:rest ?rest .
    }}"""
    return deleteCollection.format(col)


def getDropdownClasses():
    """
    Builds a query to retrieve dropdown classes as used in OntoWiki as
    well as their values
    """
    getDropdownClasses = """SELECT ?class ?elem ?pos WHERE {{
        ?class <{displayAs}> "{dropdown}" .
        OPTIONAL {{
            ?elem a ?class .
            OPTIONAL {{
                ?elem <{orderProperty}> ?pos .
            }}
        }}
    }} ORDER BY ?pos""".format(
        displayAs     = _config['dropdownDesignator']['property'],
        dropdown      = _config['dropdownDesignator']['value'],
        orderProperty = _config['orderProperty']
    )
    qres = g.query(getDropdownClasses)
    collections = {}

    for row in qres:
        a = "%s" % row[0]
        #a = re.sub(r'Value$', '', a)
        if not a in collections:
            collections[a] = []
        if row[1]:
            collections[a].append("<%s>" % row[1])

    return collections;


def deleteOWDropdowns(col):
    """
    Builds a query to delete all unwanted triples connected with a class
    col.

    arguments:
    col -- the URI of a rdf/owl class
    """
    query = """DELETE {{
        <{collection}> <{displayAs}> "{dropdown}" .
        ?elem a <{collection}> .
        ?elem <{orderProperty}> ?pos .
    }}
    WHERE {{
        OPTIONAL {{
            ?elem a <{collection}> .
            ?elem <{orderProperty}> ?pos .
        }}
    }}
    """.format(
        collection    = col,
        orderProperty = _config['orderProperty'],
        displayAs     = _config['dropdownDesignator']['property'],
        dropdown      = _config['dropdownDesignator']['value'],
    )
    return query

#
#
# main
#
#

print("loading source file '%s' as %s" % (args.file, args.input), file=sys.stderr)
print("analysing", file=sys.stderr)

g = rdflib.Graph()

# bind some namespaces that will be used in serialization
bindPrefixes(g)

# load graphparser.add_argument("echo", help="echo the string you use here")
g.parse(args.file, format=args.input)

out = "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n"

if args.mode == 'ow2git':

    collections = getDropdownClasses()

    # VERBOSE
    if args.verbose:
        print("\n(1) Retrieving all collections", file=sys.stderr)
        print("==============================\n", file=sys.stderr)

        for col, arr in collections.items():
            print("    Collection <%s> with values" % col, file=sys.stderr)
            for v in arr:
                print("        %s" % v, file=sys.stderr)

        print("", file=sys.stderr)
        print("(2) Processing collections", file=sys.stderr)
        print("==========================\n", file=sys.stderr)
        print("Query used for deleting:\n", file=sys.stderr)
        print(deleteOWDropdowns('...IRI...'), file=sys.stderr)
    else:
        print("found %d collections" % len(collections), file=sys.stderr)
        print("deleting OW specific triples", file=sys.stderr)


    for col, vals in collections.items():
        if vals:
            delete = deleteOWDropdowns(col)
            out+= "<%s> owl:oneOf (\n        %s\n      ) .\n" % (col, "\n        ".join(vals))

            # VERBOSE
            if args.verbose:
                 construct = delete.replace('DELETE {', 'CONSTRUCT {')
                 qres = g.query(construct)
                 print("Deleting <%s>" % col, file=sys.stderr)
                 print("Which means deleting:\n", file=sys.stderr)
                 print(qres.serialize(format='turtle').decode('utf-8')[:-1], file=sys.stderr)
                 print("------------------------------\n", file=sys.stderr)

            test = g.update(delete)
        else:
            print("ERROR: No values found for %s, skipping collection\n" % col, file=sys.stderr)

    # VERBOSE
    if args.verbose:
        print("(3) Adding new triples with correct notation", file=sys.stderr)
        print("============================================\n", file=sys.stderr)
        print(out, file=sys.stderr)
    else:
        print("adding nice collections", file=sys.stderr)

    gnew = rdflib.Graph()
    bindPrefixes(gnew)
    gnew.parse(io.StringIO(out), format='turtle')

    gnew += g

    print("DONE.", file=sys.stderr)

    print(gnew.serialize(format=args.output).decode('utf-8'))



if args.mode == 'git2ow':

    qres = g.query(getOwlCollections())

    # some feedback

    l = len(qres)
    if l == 0:
        print("No collection found.", file=sys.stderr)
        exit()
    else:
        print("found %d collection:" % l, file=sys.stderr)
        for row in qres:
            print("<%s>" % row, file=sys.stderr)

    # updating graph

    for row in qres:
        collClass = row[0]
        print("Processing <%s>" % collClass, file=sys.stderr)
        g.update(getDesignatorInsert(collClass))
        g.update(getOrderInsert(collClass))
        g.update(getCollectionDelete(collClass))

    # output graph

    print(g.serialize(format=args.output).decode('utf-8'))
