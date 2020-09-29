#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#
# RSS feed parser
# Version 0.2.2
# @author: nrekow
#
# Parses an RSS feed and downloads stuff.
#
# Requires lxml module to be installed (e.g. "pip install lxml").
#
# ---------------------------------------------------------------------------

from __future__ import print_function

from lxml import etree

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
	argp = argparse.ArgumentParser(description = 'RSS feed parser. Script to download stuff.')
	argp.add_argument('-o', '--output',
		dest = 'output',
		help = 'set optional output',
		default = '')
	argp.add_argument('-q', '--quiet', action = 'store_true',
		dest = 'quiet',
		help = 'enable quiet mode')
	argp.add_argument('-w', '--overwrite', action = 'store_true',
		dest = 'overwrite',
		help = 'overwrite destination file')

	args = argp.parse_args()

	return args

def main():
	# The URL of the RSS feed
	url = 'http://nauticradio.beatsnbreaks.nl/podcast/technomania'
	dest = ''

	# Parse command line parameters
	args = parse_input_arguments()

	# Check if a destination has been provided ...
	if (args.output):
		dest = args.output
	
	# Make sure there's no trailing (back)slash ...
	dest = dest.rstrip(os.sep)
	
	# ... in order to add a trailing (back)slash to have a proper path.
	dest = dest + os.sep
	
	# ... and create it if it doesn't exist.
	try:
		if dest != '.' and not(os.path.isdir(dest)):
			os.makedirs(dest)
	except OSError:
		dest = '.'

	if not args.quiet:
		print('Checking for new Nauticradio Technomania mixes ... ')

	# Fetch RSS feed
	try:
		html = ul.urlopen(url).read()
		content = etree.fromstring(html)

		# Parse RSS feed
		for item in content.xpath('/rss/channel/item'):
			link = item.xpath("./guid/text()")[0]			# Get link to video file.
			title = item.xpath("./title/text()")[0]			# Get title of video.
		
			# Cleanup title, because we'll use it as filename.
			# Keep these characters and replace everything else but a-zA-Z0-9.
			keepcharacters = (' ','.',',','-','_','&','\'',u'ä',u'ö',u'ü',u'Ä',u'Ö',u'Ü',u'ß')
			title = "".join([c for c in title if re.match(r'\w', c) or c in keepcharacters])
			title = title.replace(' - ', ' ')				# Replace separating dashes with a single space.
			title = title.replace('  ', ' ')				# Replace duplicate whitespaces with a single space.
			title = title.strip()							# Remove leading and trailing whitespaces.
			#description = item.xpath("./description/text()")[0]	# Get description of video. Just for reference.

			# Get file extension from link. Better use mime-type instead.
			ext = os.path.splitext(link)[1]
			fn = dest + title + ext
			
			# If the destination file does not exist and no overwrite flag was set, start download.
			if os.path.exists(fn) and not args.overwrite:
				if not args.quiet:
					print(title + ext + ' already exists. Skipped.')
			else:
				if not args.quiet:
					# print('Downloading ' + dest + title + ext + ' ...')
					print('Downloading', link, '... ', end='')
				
				ul.urlretrieve(link, fn)
				
				if not args.quiet:
					print('done.')
		print('')
	except URLError as e:
		print('failed with error', e.code, 'while trying to download ', url)
		sys.exit(0)
			
if __name__ == '__main__':
	main()
