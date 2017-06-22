#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# start.py: start RIPE Atlas measurements based on a JSON template
#
# Copyright (C) 2017 by Maciej Andziński <m.andzinski@gmail.com>
# Copyright (C) 2017 by Paweł Foremski <pjf@foremski.pl>
#
# Licensed under GNU GPL v3, <https://www.gnu.org/licenses/gpl-3.0.html>
#

import pycurl
import json
import time
import argparse
import random

ATLAS_URL = 'https://atlas.ripe.net/api/v2/measurements/?key=%s'

class Buff:
	def __init__(self): self.contents = ""
	def body_callback(self, buf): self.contents += buf

def main():
	prs = argparse.ArgumentParser(description='Start RIPE Atlas measurements')
	prs.add_argument('--key', help='your RIPE Atlas API key', required=True)
	prs.add_argument('--tpl', help='path to template file', required=True)
	prs.add_argument('--pbs', help='path to probe status file \
	(eg. from http://ftp.ripe.net/ripe/atlas/probes/archive/2017/04/20170419.json.bz2)', required=True)
	prs.add_argument('--out', help='path for results: the measurement ids', required=True)
	prs.add_argument('-n', type=int, default=0, help='how many probes to use')
	prs.add_argument('--step', type=int, default=1000, help='max probe count per step')
	prs.add_argument('--sleep', type=int, default=0, help='time to sleep between steps')
	prs.add_argument('--verbose', action='store_true', help='be verbose')
	prs.add_argument('-k', action='store_true', help='dry-run mode - skip any network requests')
	args = prs.parse_args()

	# read the template
	tpl = json.loads(open(args.tpl).read())

	# read the probes
	probes_data = json.loads(open(args.pbs).read())
	alive_probes = [p["id"] for p in probes_data['objects'] if p["status"] == 1]
	random.shuffle(alive_probes)
	if args.n > 0:
		alive_probes = alive_probes[0:args.n]

	# put measurement ids here
	m_ids = []

	# params
	url = ATLAS_URL % (args.key)

	# start the measurements, at most args.limit per step
	for i in range(0, len(alive_probes), args.step):
		# sleep?
		if i > 0 and args.sleep > 0:
			time.sleep(args.sleep)

		pids = alive_probes[i:i + args.step]
		print "Starting on probes %d till %d" % (i+1, i + len(pids))

		# update the template
		tpl["probes"] = [{
			"type":       "probes",
			"value":      ",".join([str(x) for x in pids]),
			"requested":  len(pids)
		}]
		if args.verbose: print json.dumps(tpl, indent=2)

		# dry mode?
		if args.k: continue

		# retry until success
		while True:
			# perform a curl query
			b = Buff()
			c = pycurl.Curl()
			c.setopt(c.WRITEFUNCTION, b.body_callback)
			c.setopt(pycurl.URL, url)
			c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])
			c.setopt(pycurl.POST, 1)
			c.setopt(pycurl.POSTFIELDS, json.dumps(tpl))
			c.perform()
			c.close()

			# read the results
			rjson = json.loads(b.contents)
			if args.verbose: print json.dumps(rjson, indent=2)

			# ok?
			if rjson.has_key("error"):
				print "Error, retrying in 1 minute..."
				time.sleep(60) # retry in 1 minute
			else:
				m_ids.extend(rjson['measurements']) # store measurement ids
				break

	# write results
	open(args.out, 'w').write(json.dumps(m_ids))

if __name__ == "__main__": main()
