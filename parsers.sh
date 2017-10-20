#!/bin/bash
#
# Bash script to run all parsers one after another.
#
# @author: nrekow
#
DESTINATION=~/Downloads/parsers
SCRIPTPATH=$(cd $(dirname $0); pwd -P)
cd $SCRIPTPATH
for i in cnh dilbert xkcd; do
	./$i/$i.py -o $DESTINATION/$i
done