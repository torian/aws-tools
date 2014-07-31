#!/usr/bin/env python
"""Usage: 
  spot-instance request -p <bid> [options]
  spot-instance status [-i <id>] [options]
  spot-instance -h|--help
  
Generic options:

  -r <region>, --region <region>  Region name [default: eu-west-1]
  --credentials FILE              Credentials file (YAML)
  -h, --help                      This help
  -v, --verbose                   Make the output verbose
  -d, --debug                     Debug information
  -n, --dry-run                   Simulate

Status options:
  -i <id>, --request-id <id>      Spot instance request id
  -e , --extended                 Show extended info if the SIR is fullfilled

Request options:
  -k <name>, --key <key_name>     Identity key name [default: eu-west-1-oe-stage]
  -p <bid>, --price <bid>         Spot instance bid
  -t <type>, --type <type>        Instance type [default: t1.micro]
  -a <ami_id>, --ami-id <ami_id>  AMI id [default: ami-8337f8f4]
  -c COUNT, --count COUNT         Number of instances to launch [default: 1]
  -z <av_zone>, --zone <av_zone>  Availability zone [default: eu-west-1a]
  -s <sg>, --sec-group <sg>       Security group
  -S <subnet>, --subnet <subnet>  Subnet ID

"""

from   docopt import  docopt

import boto
import boto.regioninfo
import boto.ec2

import sys
import os
import yaml
from   pprint import pprint

###############################################################################

def get_status(c = None, rids = [], filters = {}, extended = False):
  if c is None:
    return false 

  spot_instances = c.get_all_spot_instance_requests(
    request_ids = rids, 
    filters = filters
  )
  for i in spot_instances:
    print "%s:" % i.id 
    print "  %s %s %s %s %s %s %s %s" % (
      i.instance_id, 
      i.price, 
      i.state, 
      i.status, 
      i.create_time, 
      i.tags, 
      i.launched_availability_zone, 
      i.launch_specification
    )

    if extended:
      #nfo = boto.ec2.instanceinfo.InstanceInfo(c, i.instance_id)
      reservations = c.get_all_instances(i.instance_id)
      instances    = [ i for r in reservations for i in r.instances ]
      for i in instances:
        pprint(i.__dict__)
        


def request_instance(c = None, o = None):
  if c is None:
    return false

  request = c.request_spot_instances(
    o['price'],
    image_id      = o['ami-id'],
    key_name      = o['key'],
    count         = o['count'],
    instance_type = o['type'],
    subnet_id     = o['subnet'],
    placement     = o['zone'],
  )

  print request

###############################################################################

# Options from __doc__
opts = docopt(__doc__)
options = {}

cfg = {
  'subnet':    'subnet-4da5e325',
  'sec-group': 'sg-07af4b68'
}

# Set some defaults
for o in opts:
  key = o.strip('-')

  if key in cfg and not opts[o]:
    options[key] = cfg[key]
  else:
    options[key] = opts[o]
 
# Debugging of options
if options['debug']:
  pprint(options)

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

if options['verbose']:
  print "Region: %s" % options['region']

region = boto.ec2.get_region(options['region'])

if credentials:
  conn = boto.connect_ec2(
    aws_access_key_id     = credentials['aws_access_key_id'],
    aws_secret_access_key = credentials['aws_secret_access_key'],
    region                = region
  )
else:
  conn = boto.connect_ec2(region = region)

if conn is None:
  print "Could not connect to region %s" % options['region']
  sys.exit(1)

if options['status']:
  get_status(conn, options['request-id'], {}, options['extended'])

if options['request']:
  request_instance(conn, options)

