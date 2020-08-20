#!/usr/bin/env python2
# encoding: utf8
from __future__ import print_function
import os, sys, json, urllib2

# Before v2.5 the repo was under a different URL (rsms/interface).
# This is the last known download count of that old repo.
pre_v2_5_count = 81218

f = urllib2.urlopen('https://api.github.com/repos/rsms/inter/releases')
releases = json.load(f)

# find longest name
maxNameLen = 0
for release in releases:
  if len(release['assets']) > 0:
    maxNameLen = max(maxNameLen, len(release['tag_name']))

# print download count per version and count total
countTotal = pre_v2_5_count
for release in releases:
  if len(release['assets']) > 0:
    count = release['assets'][0]['download_count']
    countTotal += count
    print('%-*s  %d' % (maxNameLen, release['tag_name'], count))
  else:
    print('%-*s  (missing)' % (maxNameLen, release['tag_name']))

print('%-*s  %d' % (maxNameLen, '<v2.5', pre_v2_5_count))
print(('—' * maxNameLen) + '  ' + ('—' * maxNameLen))
print('%-*s  %d' % (maxNameLen, 'Total', countTotal))
