#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# merge.py: merge RIPE Atlas collected with collect.py
#
# Copyright (C) 2017 by Maciej Andziński <m.andzinski@gmail.com>
# Copyright (C) 2017 by Paweł Foremski <pjf@foremski.pl>
#
# Licensed under GNU GPL v3, <https://www.gnu.org/licenses/gpl-3.0.html>
#


import json
import sys
import argparse

def main():
	prs = argparse.ArgumentParser(description='Merge RIPE Atlas measurements')
	prs.add_argument('--out', help='start.py output file (measurement ids)', required=True)
	prs.add_argument('--dir', help='collect.py output directory (measurement results)', required=True)
	args = prs.parse_args()

	results = []

	# for each measurement id (mid)
	for mid in json.loads(open(args.out).read()):
		fh = open("%s/%d.json" % (args.dir, mid))
		res = json.loads(fh.read())
		results.extend(res)

	print json.dumps(results, indent=2)

if __name__ == "__main__": main()
