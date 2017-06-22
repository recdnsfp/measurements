#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# collect.py: collect RIPE Atlas measurements started by start.py
#
# Copyright (C) 2017 by Maciej Andziński <m.andzinski@gmail.com>
# Copyright (C) 2017 by Paweł Foremski <pjf@foremski.pl>
#
# Licensed under GNU GPL v3, <https://www.gnu.org/licenses/gpl-3.0.html>
#

import json
import urllib2
import sys
import argparse

ATLAS_URL = "https://atlas.ripe.net/api/v2/measurements/%d/results?key=%s"

def main():
	prs = argparse.ArgumentParser(description='Collect RIPE Atlas measurements')
	prs.add_argument('--key', help='your RIPE Atlas API key', required=True)
	prs.add_argument('--out', help='start.py output file (measurement ids)', required=True)
	prs.add_argument('--dir', help='output directory (must exist)', required=True)
	prs.add_argument('--verbose', action='store_true', help='be verbose')
	prs.add_argument('-k', action='store_true', help='dry-run mode - skip any network reqs')
	args = prs.parse_args()

	# for each measurement id (mid)
	for mid in json.loads(open(args.out).read()):
		print "Fetching result %d..." % (mid)

		# prepare
		url = ATLAS_URL % (mid, args.key)
		if args.verbose: print url
		if args.k: continue

		# make request
		req = urllib2.Request(url)
		req.add_header("Accept", "application/json")
		conn = urllib2.urlopen(req)

		# parse
		r = json.load(conn)
		rs = json.dumps(r, indent=2)
		if args.verbose: print rs

		# write
		fh = open("%s/%d.json" % (args.dir, mid), "w")
		fh.write(rs)

if __name__ == "__main__": main()
