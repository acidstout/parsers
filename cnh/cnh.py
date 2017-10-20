#!/usr/bin/env python
# ---------------------------------------------------------------------------
#
# Cyanide & Happiness Parser
# Version 0.3.1
# @author: nrekow
#
# Allows to specify start and end id of comic strips as well as download folder.
# Defaults to first known comic strip id as start id.
# Gets the id of the latest comic strip as end id.
# Creates download folder if it doesn't exist.
# Creates a list of invalid comic ids in order to speed up resuming an aborted download.
#
# ---------------------------------------------------------------------------

from __future__ import print_function

import os
import glob
import re
import sys
import argparse
import time

if sys.version_info[0] <= 2:
	print('This script requires Python 3 to run.')
	sys.exit(0)

# For checking the image type of a file (e.g. gif, jpeg, ...)
try:
	import imghdr
except ImportError:
	print('This script requires the imghdr module to be installed.')
	sys.exit(0)

# For catching URLError while trying to download comic strip
try:
	from urllib.error import URLError
	import urllib.request as ul
except ImportError:
	print('This script requires the urllib2 module to be installed.')
	sys.exit(0)


def main():
	# Parse command line arguments
	args = parse_input_arguments()

	# Get path to this script
	script_path = os.path.abspath(os.path.dirname(__file__))

	# If the download folder does not exist, create it ...
	try:
		if args.output != '.' and not(os.path.isdir(args.output)):
			os.makedirs(args.output)
	except OSError:
		args.output = '.'
	
	# ... and move to it
	os.chdir(args.output)
	
	# Download comic strips
	try:
		download_strips(script_path, args.start_image, args.end_image)
	except (KeyboardInterrupt, SystemExit):
		print('User requested program exit.')
		sys.exit(1)
	
	print('\n')


def parse_input_arguments():
	# Parses command line arguments and sets default values if an argument is omitted.
	argp = argparse.ArgumentParser(description = 'Cyanide & Happiness Parser. Script to download Cyanide & Happiness comic strips.')
	argp.add_argument('-s', '--start',
		help = 'start image (15, 1st published strip).',
		dest = 'start_image',
		default = '15')
	argp.add_argument('-e', '--end',
		dest = 'end_image',
		help = 'End image (default, latest)',
		default = '0')
	argp.add_argument('-o', '--output',
		dest = 'output',
		help = 'Comics dump folder',
		default = '.')

	args = argp.parse_args()
	
	# Get id of latest comic strip
	if int(args.end_image) == 0:
		args.end_image = get_latest_comic_id()
		if int(args.end_image) == 0:
			args.end_image = '5000' # Fallback to 5000. In the future this will not be enough. Maybe increase or optimize.
		
	print('Latest comic id:', args.end_image)
	# Only check for today's comic strip? Then use now as start and end date.
	print('Checking if new Cyanide & Happiness content is available ...')

	return args


def download_strips(script_path, start_image, end_image):
	# Gets a list of already downloaded comics
	comics = glob.glob('./*')
	
	# Will contain only the filenames (dates of the comic) without the actual file extension.
	comics_filenames = []
	
	# Will contain the missing comics
	missing_comics = []

	# Extract filename (cut-off extension)
	for comic in comics:
		base = os.path.basename(comic)
		comics_filenames.append(os.path.splitext(base)[0])

	# Read log file and append invalid comic ids to the comics_filename array in order to skip processing of them.
	try:
		print('Using data file ' + os.path.join(script_path, 'cnh.dat'))
		fh = open(os.path.join(script_path, 'cnh.dat'), 'r')
		if fh:
			for line in fh:
				line = line.replace('\n','')
				if line != '':
					comics_filenames.append(line)
			fh.close()
	except:
		print('Data file not found.')

	# Check defined date range if the file already exists
	for i in range(int(start_image), int(end_image)+1):
		if str(i) in comics_filenames:
			# Remove existing entries from the list to speed up next check
			comics_filenames.remove(str(i))
		else:
			# Only add missing images to the list
			missing_comics.append(str(i))
	
	# In case we have comics missing, try to download them.
	if missing_comics:
		for comic_date in missing_comics:
			# Build URL to comic strip page
			url  = 'http://explosm.net/comics/' + comic_date
			
			# Save the file as tmp-file, because we don't know the image type, yet.
			comic_name = comic_date + '.tmp'
		
			# Don't add a line feed to the end of the string.
			# Also mind that concatenating strings this way will add a space
			# to the beginning of the second string after adding the variable.
			print('Getting comic', comic_date, end='')

			download_ok = False
			comic_url = ''
			
			try:
				comic_url = get_true_comic_url(url)
				
				if comic_url != '':
					# comic_url = comic_url.replace(' ', '%20')
					print(' from', comic_url, '... ', end='')
					ul.urlretrieve(comic_url, comic_name)
					# Sleep a little to avoid hammering the server.
					time.sleep(0.01)
					print('ok!')
					download_ok = True
				else:
					print(' not found!')
					try:
						fh = open(os.path.join(script_path, 'cnh.dat'), 'a')
						if fh:
							fh.write(comic_date + '\n')
							fh.close()
					except:
						print('Cannot create data file!')
			except URLError as e:
				errMsg = ' failed with error ' + str(e.code) + ' while trying to download ' + url
				fh = open(os.path.join(script_path, 'cnh.log'), 'a')
				if fh:
					fh.write(errMsg + '\n')
					fh.close()
				
				print(errMsg)
				print('Will try again after 10 seconds ... ', end='')

				time.sleep(10.0)
				
				if e.code != 404:
					try:
						comic_url = get_true_comic_url(url)
						if comic_url != '':
							# comic_url = comic_url.replace(' ', '%20')
							ul.urlretrieve(comic_url, comic_name)
							# Sleep a little to avoid hammering the server.
							time.sleep(0.01)
							print('ok!')
							download_ok = True
						else:
							print('not found!')
					except URLError as e:
						errMsg = 'failed with error ' + str(e.code) 
						fh = open(os.path.join(script_path, 'cnh.log'), 'a')
						if fh:
							fh.write(errMsg + ' while trying to download ' + url + '\n')
							fh.close()

						print(errMsg, end='')
						print('. Skipping.')
				
			if download_ok:
				# nrekow, 2017-02-02: Check image type and set proper file extension.
				extension = imghdr.what(comic_name)
					
				if extension is not None:
					try:
						os.rename(comic_name, comic_name[:-3] + extension)
					except OSError:
						print('Cannot change file extension of', comic_name)
	else:
		print('No new content available, yet.')


def get_true_comic_url(comic_url, comic_name='comic'):
	"""
	Get the true comic strip url from http://dilbert.com/strip/<date>

	It looks like Scott Adams has protected himself against pointy haired
	pirates by hiding his comic strips within the assets.amuniversal domain.
	This function digs into the comic strip web-page, finds (and returns)
	the URL where the original image lives.
	"""

	html = str(ul.urlopen(comic_url).read())
	comic_strip_pattern = 'http:\/\/files\.explosm\.net\/comics\/[a-zA-Z\d\.\(\)\-\/_\,\!\@\s\%]+'
	result = re.search(comic_strip_pattern, html)
	if result:
		return result.group()
	else:
		return ''


def get_latest_comic_id():
	"""
	Get the id of the latest comic strip from http://explosm.net/comics/latest
	
	Checks HTML head for content of meta property tag and cleans up result.
	"""
	html = str(ul.urlopen('http://explosm.net/comics/latest').read())
	comic_id_pattern = '<meta property="og:url" content="http:\/\/explosm\.net\/comics\/[0-9]+\/">'
	result = re.search(comic_id_pattern, html)
	if result:
		result = result.group()
		result = re.sub("\D", "", result)
		return result
	else:
		return '0'


if __name__ == '__main__':
	main()
