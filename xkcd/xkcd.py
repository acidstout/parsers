#!/usr/bin/env python
"""
Download all the comic strips listed in the XKCD archive page.

Author: nrekow

Based on the work of Alvaro. See https://gist.github.com/apadi/3a2c6ca53611f610a4fd for details.
"""

from __future__ import print_function

import glob
import os
import re
import sys
import argparse

if sys.version_info[0] <= 2:
	print('This script requires Python 3 to run.')
	sys.exit(0)

try:
	from urllib.error import URLError
	import urllib.request as ul
except ImportError:
	print('This script requires the urllib module to be installed.')
	sys.exit(0)

try:
	import imghdr
except ImportError:
	print('This script requires the imghdr module to be installed.')
	sys.exit(0)


def main():
	args = parse_input_arguments()

	script_path = os.path.abspath(os.path.dirname(__file__))

	# If a dump folder has been defiled, create it (if does not already exists)
	# and move to it
	try:
		if args.output != '.' and not(os.path.isdir(args.output)):
			os.makedirs(args.output)
	except OSError:
		args.output = '.'

	os.chdir(args.output)

	try:
		get_xkcd_strips(script_path)
	except (KeyboardInterrupt, SystemExit):
		print('User requested program exit.')
		sys.exit(1)
	
	print('\n')


def parse_input_arguments():
	argp = argparse.ArgumentParser(description = 'XKCD Parser. Script to download XKCD comic strips.')
	argp.add_argument('-o', '--output',
		dest = 'output',
		help = 'Comics dump folder',
		default = '.')

	args = argp.parse_args()
	
	# Only check for today's comic strip? Then use now as start and end date.
	print('Checking if new XKCD content is available ...')

	return args


def get_xkcd_strips(script_path):
	"""
	Connect to the XKCD index page and return a dict with all the available
	comic strips and its URL.
	"""
	
	# Use https
	xkdc_index=str(ul.urlopen('https://xkcd.com/archive/').read())

	# Extended the search pattern by more characters to fix support for multiple images and their title.
	xkcd_strip_pattern = '<a href="/(?P<strip_id>\d+)/" title="(?P<date>[\d-]+)">(?P<title>[\w\s\d\.\-\/\[\]\(\)\_]+)</a><br/>'

	xkcd_strips_url = re.findall(xkcd_strip_pattern, xkdc_index)

	for xkcd_strip in xkcd_strips_url:
		get_comic_image(script_path, '_'.join(xkcd_strip), 'https://xkcd.com/' + xkcd_strip[0])


def get_comic_image(script_path, comic_name, comic_url):
	# Replace slashes in comic name by underscores
	comic_name = comic_name.replace('/','_')
	comic_name = comic_name.replace('\\','_')
	
	# Check if image already exists on harddisk
	if not glob.glob(comic_name + '.*'):
		'''
		print('skipped existing file', comic_name)
		else:
		'''
		print('checking', comic_url, '... ', end='')
		html = str(ul.urlopen(comic_url).read())
		
		# Modified pattern to be more generic.
		strip_pattern = '//imgs\.xkcd\.com/comics/[\w\d\.\/\(\)\-\_]+'
		
		image_url = re.search(strip_pattern, html)
		if image_url:
			image_url = image_url.group()
		
		# Workaround for generated live image
		if comic_url.endswith('1446'):
			image_url = '//imgs.xkcd.com/comics/landing/awake.png'
		
		if image_url:
			print('ok')
			download_ok = False
			print('downloading', 'https:' + image_url, '... ', end='')
			
			# Try to download the image and save it as tmp-file.
			try:
				ul.urlretrieve('https:' + image_url, comic_name + '.tmp')
				print('ok')
				download_ok = True
			except URLError as e:
				errMsg = 'failed with error ' + e.code + '. Unable to obtain image from: ' + 'https:' + image_url
				print(errMsg)
				fh = open(os.path.join(script_path, 'xkcd.log'), 'a')
				if fh:
					fh.write(errMsg + '\n')
					fh.close()


			if download_ok:
				# Check filetype and rename extension
				extension = imghdr.what(comic_name + '.tmp')
					
				if extension is not None:
					try:
						os.rename(comic_name + '.tmp', comic_name + '.' + extension)
					except OSError:
						errMsg = 'Cannot change file extension of' + comic_name + '.tmp'
						print (errMsg)
						fh = open(os.path.join(script_path, 'xkcd.log'), 'a')
						if fh:
							fh.write(errMsg + '\n')
							fh.close()
		else:
			# Images 1608 and 1663 cannot be downloaded, because those are interactive comic strips.
			if comic_url.endswith('1608') or comic_url.endswith('1663'):
				print('interactive comic-strips are not supported.')
			else:
				print('no comic found.')


if __name__ == '__main__':
	main()