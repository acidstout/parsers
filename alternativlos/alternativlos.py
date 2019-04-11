#!/usr/bin/env python
"""
Alternativlos Parser
See README.md for details.

Author: nrekow
"""

from urllib.parse import urlparse
from pathlib import Path
import os
import sys
import argparse

if sys.version_info[0] <= 2:
	print('This script requires Python 3 to run.')
	sys.exit(0)

try:
	from xml.dom.minidom import parse, parseString
except ImportError:
	print('This script requires the xml.dom/minidom module to be installed.')
	sys.exit(0)

try:
	from urllib.error import URLError
	import urllib.request as ul
except ImportError:
	print('This script requires the urllib module to be installed.')
	sys.exit(0)


def parse_input_arguments():
	argp = argparse.ArgumentParser(description = 'Alternativlos Parser.')
	argp.add_argument('-o', '--output',
		dest = 'output',
		help = 'Podcasts dump folder',
		default = '.')
	args = argp.parse_args()
	return args


def main():
	args = parse_input_arguments()
	try:
		if args.output != '.' and not(os.path.isdir(args.output)):
			os.makedirs(args.output)
	except OSError:
		args.output = '.'
	
	script_path = os.path.abspath(os.path.dirname(__file__))
	
	os.chdir(args.output)

	url = 'https://alternativlos.org/alternativlos.rss'
	html = str(ul.urlopen(url).read(), 'utf-8')
	
	xmldoc = parseString(html)
	itemlist = xmldoc.getElementsByTagName('enclosure')
	has_new_podcasts = False;

	print('Checking if new Alternativlos podcasts are available ... ', end='')
	
	for s in itemlist:
		destination_name = urlparse(s.attributes['url'].value)
		destination_name = os.path.join(args.output, os.path.basename(destination_name.path))
		destination_path = Path(destination_name) 

		if not destination_path.exists():
			if not has_new_podcasts:
				print('ok.')
				has_new_podcasts = True
				
			print('Downloading', s.attributes['url'].value, '... ', end='')
			try:
				ul.urlretrieve(s.attributes['url'].value, destination_name)
				print('ok')
			except URLError as e:
				errMsg = 'failed with error ' + e.code + '. Unable to obtain file from: ' + s.attributes['url'].value
				print(errMsg)
				fh = open(os.path.join(script_path, 'alternativlos.log'), 'a')
				if fh:
					fh.write(errMsg + '\n')
					fh.close()

	if not has_new_podcasts:
		print('nothing new.')
		
if __name__ == '__main__':
	main()
