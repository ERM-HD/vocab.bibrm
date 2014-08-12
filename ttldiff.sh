#!/bin/bash
#
# This scrict compares to turtle files displays differences. This is done by
# converting both turtle files to ntriples, sorting them and then using a
# conventional diff or (if available: colordiff)
#
# There is a problem with blank nodes: As blank nodes can only be compared
# by checking the structure of the triples in which they occur, any blank
# nodes are currently ignored.
#
# Usage:
#    ttldiff.sh turtlefile1 turtlefile2
#
# Copyright:    (c) 2013 AKSW <http://aksw.org/>
# License:      GNU General Public License (GPL) <http://opensource.org/licenses/gpl-license.php>
# Author:       Andreas Nareike <http://aksw.org/AndreasNareike>

smartdiff() {
    if hash colordiff 2>/dev/null; then
        colordiff "$@"
    else
        diff "$@"
    fi
}

smartdiff -I genid <((rapper $1 -i turtle -o ntriples | sort -u) 2> /dev/null) \
                   <((rapper $2 -i turtle -o ntriples | sort -u) 2> /dev/null)
