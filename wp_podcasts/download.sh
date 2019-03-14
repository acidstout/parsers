#!/bin/bash
DEST="./articles"
SRCLIST="articles.txt"

if [ -f "$SRCLIST" ]; then
	if [ ! -d "$DEST" ]; then
		mkdir "$DEST"
	fi
	
	wget --background --continue --timestamping --quiet --directory-prefix="$DEST" -i "$SRCLIST"
else
	echo "Error: configured source list file does not exist."
fi