#!/usr/bin/env python
"""
Dilbert Parser
See README.md for details.
"""

from __future__ import print_function
from http.client import RemoteDisconnected
from urllib.error import HTTPError

# Set duration in seconds to wait after each download to avoid hammering the server
wait = 2

#####################################################################################


import datetime
import os
import glob
import re
import sys
import time
import argparse

import requests
import codecs


if sys.version_info[0] <= 2:
	print('This script requires Python 3 to run.')
	sys.exit(0)
	
# nrekow, 2017-02-10:
try:
	from dateutil import rrule, parser
except ImportError:
	print('This script requires the dateutil module to be installed.')
	sys.exit(0)

# nrekow, 2017-02-02:
try:
	import imghdr
except ImportError:
	print('This script requires the imghdr module to be installed.')
	sys.exit(0)

# nrekow, 2017-02-10:	
try:
	from urllib.error import URLError
	import urllib.request as ul
except ImportError:
	print('This script requires the urllib module to be installed.')
	sys.exit(0)


def main():
	args = parse_input_arguments()

	# If a dump folder has been defiled, create it (if does not already exists)
	# and move to it

	try:
		if args.output != '.' and not(os.path.isdir(args.output)):
			os.makedirs(args.output)
	except OSError:
		args.output = '.'
	
	script_path = os.path.abspath(os.path.dirname(__file__))
	
	os.chdir(args.output)

	try:
		download_strips(script_path, args.start_date, args.end_date)
	except (KeyboardInterrupt, SystemExit):
		print('User requested program exit.')
		sys.exit(1)

	print('\n')


def parse_input_arguments():
	argp = argparse.ArgumentParser(description = 'Dilbert Parser. Script to download Dilbert comic strips.')
	argp.add_argument('-s', '--start',
		help = 'start date (1989-04-17, 1st published strip).',
		dest = 'start_date',
		default = '1989-04-17')
	argp.add_argument('-e', '--end',
		dest = 'end_date',
		help = 'End date (default, today)',
		default = None)
	argp.add_argument('-o', '--output',
		dest = 'output',
		help = 'Comics dump folder',
		default = '.')

	args = argp.parse_args()
	if args.end_date is None:
		args.end_date = datetime.datetime.now().date()
	else:
		args.end_date = parser.parse(args.end_date)
	
	args.start_date = parser.parse(args.start_date)
	
	# Only check for today's comic strip? Then use now as start and end date.
	print('Checking if new Dilbert content is available ...')

	return args


def is_date(string):
    try: 
        parser.parse(string)
        return True
    except ValueError:
        return False


def download_strips(script_path, start_date, end_date):
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

	# Check defined date range if the file already exists
	for date in list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date)):
		comic_date = '%04d-%02d-%02d' % (date.year, date.month, date.day)
		
		if comic_date in comics_filenames:
			# Remove existing entries from the list to speed up next check
			comics_filenames.remove(comic_date)
		else:
			# Only add dates to the list
			if is_date(comic_date):
				missing_comics.append(comic_date)
	
	# In case we have comics missing, try to download them.
	if missing_comics:
		for comic_date in missing_comics:
			# Build URL to comic strip page
			url  = 'http://dilbert.com/strip/' + comic_date

			# Save the file as tmp-file, because we don't know the image type, yet.
			comic_name = comic_date + '.tmp'
		
			# Don't add a line feed to the end of the string.
			# Also mind that concatenating strings this way will add a space
			# to the beginning of the second string after adding the variable.
			print('Getting comic from', comic_date, '... ', end='')

			download_ok = False
			try:
				try:
					ul.urlretrieve(get_true_comic_url(script_path, url), comic_name)
					# Sleep a little to avoid hammering the server.
					time.sleep(wait)
					print('ok!')
					download_ok = True
				except RemoteDisconnected as r:
					print('Remote end closed connection without response.')
			except HTTPError as e:
				print('failed with error' + str(e.code))
			except URLError as e:
				print('failed with error', e.args, 'while trying to download ', url)
				print('Will try again after 10 seconds ... ', end='')
				time.sleep(10.0)
				
				try:
					ul.urlretrieve(get_true_comic_url(script_path, url), comic_name)
					# Sleep a little to avoid hammering the server.
					time.sleep(wait)
					print('ok!')
					download_ok = True
				except HTTPError as e:
					errMsg = 'failed with error' + str(e.code)
				except URLError as e:
					errMsg = 'failed with error' + str(e.args)
					fh = open(os.path.join(script_path, 'dilbert.log'), 'a')
					if fh:
						fh.write(errMsg + ' while trying to download ' + url + '\n')
						fh.close()
						
					print(errMsg, end='')
					print('. Skipping.')

			if download_ok:
				# nrekow, 2017-02-02: Check image type and set proper file extension.
				try:
					extension = imghdr.what(comic_name)
					if extension is not None:
						try:
							os.rename(comic_name, comic_name[:-3] + extension)
						except OSError:
							print('Cannot change file extension of', comic_name)

				except FileNotFoundError:
					print('Cannot check file type of non-existent files.')
	else:
		print('No new content available, yet.')


def get_true_comic_url(script_path, comic_url, comic_name='comic'):
	"""
	Get the true comic strip url from http://dilbert.com/strip/<date>

	It looks like Scott Adams has protected himself against pointy haired
	pirates by hiding his comic strips within the assets.amuniversal domain.
	This function digs into the comic strip web-page, finds (and returns)
	the URL where the original image lives.
	"""

	try:
		html = str(ul.urlopen(comic_url).read())
		comic_strip_pattern = 'http://assets\.amuniversal\.com/[a-zA-Z\d]+'
		return re.search(comic_strip_pattern, html).group()
	except HTTPError as e:
		errMsg = 'failed with error' + str(e.code)
	except URLError as e:
		errMsg = 'Failed with error' + str(e.args) + 'while trying to get true comic url from ' + comic_url
		fh = open(os.path.join(script_path, 'dilbert.log'), 'a')
		if fh:
			fh.write(errMsg + '\n')
			fh.close()

		print(errMsg, end='')
		print('. Skipping.')


if __name__ == '__main__':
	main()
