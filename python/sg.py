#!/usr/bin/env python
"""Usage: 
  sg.py list [options]
  sg.py show (-i SG_ID|-n SG_NAME) [options]
  sg.py add-rule (-i SG_ID|-n SG_NAME) [-P PROTO] [-f PORT] -t PORT --ip IP [options]

Generic options:
  -r REGION, --region REGION    Region name [default: us-east-1]
  --credentials FILENAME        Credentials file in YAML format
  -v, --verbose                 Show verbose output [default: False]
  -d, --debug                   Debug messages

Show options:
  -i SG_ID, --id SG_ID          Security group ID
  -n SG_NAME, --name SG_NAME    Security group name

Add rule options:
  -P PROTO, --protocol PROTO    Protocol [default: tcp]
  -f PORT, --from_port PORT     From port
  -t PORT, --to_port PORT       To port
  --ip IP                       IP range
"""

###############################################################################

from   docopt import  docopt

import boto
import boto.regioninfo
import boto.ec2

import os
import yaml

from   pprint import pprint

###############################################################################

opts = docopt(__doc__)

# Some defaults
cfg     = {}

options = {}

# Set some defaults and strip dashes
for o in opts:
  key = o.strip('-')

  if key in cfg and not opts[o]:
    options[key] = cfg[key]
  else:
    options[key] = opts[o]
 
if options['debug']:
  print options

# If a credentials file is passed, load it
# It must be in YAML format, with two values:
#  - aws_access_key_id
#  - aws_secret_access_key

credentials = False
if options['credentials']:
  if options['verbose']:
    print ' Loading credentials from %s' % options['credentials']
  try:
    fh = open(os.path.abspath(options['credentials']), 'r')
    credentials = yaml.load(fh)
    fh.close()
    
    if options['debug']:
      print ' Access key id:     %s' % credentials['aws_access_key_id']
      print ' Secret Access key: %s' % credentials['aws_secret_access_key']
  except Exception as msg:
    print msg
    exit(1)

region = boto.ec2.get_region(options['region'])

if credentials:
  connection = boto.connect_ec2(
    aws_access_key_id     = credentials['aws_access_key_id'],
    aws_secret_access_key = credentials['aws_secret_access_key'],
    region                = region
  )
else:
  connection = boto.connect_ec2(region = region)


if options['list']:
  security_groups = connection.get_all_security_groups()
  for s in [ sg for sg in security_groups ]:
    print " %s / %s" % (s.name, s.id)

if options['show']:
  if options['id']:
    sg = connection.get_all_security_groups(
      group_ids = [ options['id'], ]
    )[0]
    #sg = [ i for i in security_groups if i.id == options['id'] ][0]
  elif options['name']:
    sg = connection.get_all_security_groups(
      groupnames = [ options['name'], ]
    )[0]
    #sg = [ i for i in security_groups if i.name == options['name'] ][0]

  print "name: %s" % sg.name
  print "id: %s"   % sg.id
  print "rules:"
  print "   proto/port\tIP"
  for r in sg.rules:
    # If from and to port are the same, no need to be redundant on output
    if r.from_port == r.to_port:
      port = r.to_port
    else:
      port = '%s-%s' % (r.from_port, r.to_port)

    print " - %s/%s\t%s" % (port, r.ip_protocol, r.grants)

if options['add-rule']:
  if options['id']:
    sg = connection.get_all_security_groups(
      group_ids = [ options['id'], ]
    )[0]
  elif options['name']:
    sg = connection.get_all_security_groups(
      groupnames = [ options['name'], ]
    )[0]

  if not options['from_port']:
    options['from_port'] = options['to_port']
  
  sg.authorize(
    ip_protocol = options['protocol'],
    from_port   = options['from_port'],
    to_port     = options['to_port'],
    cidr_ip     = options['ip'],
  )
