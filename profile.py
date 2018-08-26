#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv

MAX_TEMP = 240
MIN_TEMP = 40

def get_profile_path_from_args(argv):
	try:
		index = argv.index('--profile')
	except:
		return None

	if (index > 0):
		param = argv[index + 1]

		if param != None:
			return param

	return None

def read_profile_csv(path):
	profile = []
	if path == None:
		path = "./profile.csv"

	try:
		with open(path, 'rb') as f:
			reader = csv.reader(f)
			try:
				for row in reader:
					checkpoint = {
						"minute": float(row[0]),
						"temp": float(row[1])
					}
					profile.append(checkpoint.copy())
			except csv.Error as e:
				sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
	except IOError:
		print "File: " + path + " Not Found."
		sys.exit(1)

	profile = {v['minute']:v for v in profile}.values()
	return sorted(profile, key=lambda p: p['minute'])

def profile(argv):
	path = get_profile_path_from_args(argv)
	return read_profile_csv(path)

if __name__ == "__main__":
  print profile(sys.argv)
