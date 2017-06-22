#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# ---------------------------------------------------------------------------
#
# c't Uplink RSS video feed parser
# Version 0.2
# @author: nrekow
#
# Parses the HD video RSS feed and creates a Bash/Batch script with wget
# entries for each video. Videos will be stored using the respective title
# as found in the parsed RSS feed.
#
#
# ---------------------------------------------------------------------------

from __future__ import print_function

from lxml import etree

import urlparse
import platform
import os
import re
import sys
import codecs
import argparse

if sys.version_info[0] <= 2:
	print('This script requires Python 3 to run.')
	sys.exit(0)


# For catching URLError while trying to download comic strip
try:
	from urllib.error import URLError
	import urllib.request as ul
except ImportError:
	print('This script requires the urllib module to be installed.')
	sys.exit(0)

# for backwards compatibility

def parse_input_arguments():
	argp = argparse.ArgumentParser(description = 'c\'t Uplink Parser. Script to download videos.')
	argp.add_argument('-q', '--quiet', action = 'store_true',
		dest = 'quiet',
		help = 'enable wget quiet mode')
	argp.add_argument('-o', '--overwrite', action = 'store_true',
		dest = 'overwrite',
		help = 'overwrite destination file')

	args = argp.parse_args()

	return args

def main():
	# The URL of the c't Uplink RSS video feed
	url = 'https://www.heise.de/ct/uplink/ctuplinkvideohd.rss'

	# Fetch RSS feed
	try:
		html = str(ul.urlopen(url).read())
		ctuplink = etree.fromstring(html)
		
		# Check OS and decide what type of file to create
		if platform.system() == 'Windows':
			script_ext = '.cmd'
			script_first = '@echo off\n'
		else:
			script_ext = '.sh'
			script_first = '#!/bin/bash\n'
	
		filename = 'ctuplink' + script_ext
		
		# Parse command line parameters
		args = parse_input_arguments()
		
		# Flag to decide whether wget is quiet or not. Defaults to not quiet.
		if args.quiet:
			quiet = '--quiet ' # Mind the trailing space.
		else:
			quiet = ''
			
		# Set write mode depending on file existence or parameter
		if args.overwrite:
			mode = 'w'	# Overwrite
		else:
			if os.path.exists(filename):
				mode = 'a'	# Append
			else:
				mode = 'w'	# Create
		
		fh = codecs.open(filename, mode, "iso-8859-1")
		if fh:
			# Add predefined first line to script
			if mode == 'w':
				fh.write(script_first)
			
			# Parse RSS feed
			for item in ctuplink.xpath('/rss/channel/item'):
				link = item.xpath("./guid/text()")[0]				# Get link to video file.
				
				# If the current URL does not exist in the destination file add it.
				if link not in open(filename).read():
					title = item.xpath("./title/text()")[0]			# Get title of video.
				
					# Cleanup title, because we'll use it as filename.
					# Keep these characters and replace everything else but a-zA-Z0-9.
					keepcharacters = (' ','.',',','-','_','&','\'',u'ä',u'ö',u'ü',u'Ä',u'Ö',u'Ü',u'ß')
					title = "".join([c for c in title if re.match(r'\w', c) or c in keepcharacters])
					title = title.replace('c\'t uplink ','')		# Also remove the "c't uplink" ...
					title = title.replace('c\'t Episode ', '')		# ... and "c't Episode" from the title.
					title = title.replace(' - ', ' ')			# Replace separating dashes with a single space.
					title = title.replace('  ', ' ')			# Replace duplicate whitespaces with a single space.
					title = title.strip()					# Remove leading and trailing whitespaces.
					#description = item.xpath("./description/text()")[0]	# Get description of video. Just for reference.
	
					# Get file extension from link. Better use mime-type instead.
					path = urlparse.urlparse(link).path
					ext = os.path.splitext(path)[1]
					
					try:
						# Generate a bash/batch file which contains one wget entry per link.
						message = u'wget --continue --timestamping --referer="' + url + '" ' + quiet + '--output-document="' + title + ext + '" ' + link + '\n'
						fh.write(message)
					except:
						print('Cannot write to file!')
			fh.close()
		else:
			print('Cannot open file for writing!')
	except URLError as e:
		print('failed with error', e.code, 'while trying to download ', url)
		sys.exit(0)
			
if __name__ == '__main__':
	main()
