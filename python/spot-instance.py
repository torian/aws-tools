#!/usr/bin/env python
"""Usage: 
  spot-instance request -p <bid> [options]
  spot-instance status [-i <id>] [options]
  spot-instance -h|--help
  
Generic options:

  -h, --help                      This help
  -v, --verbose                   Make the output verbose
  -d, --debug                     Debug information
  -n, --dry-run                   Simulate
  -r <region>, --region <region>  Region name [default: eu-west-1]

Status options:
  -i <id>, --request-id <id>      Spot instance request id

Request options:
  -k <name>, --key <key_name>     Identity key name [default: some-key]
  -p <bid>, --price <bid>         Spot instance bid
  -t <type>, --type <type>        Instance type [default: t1.micro]
  -a <ami_id>, --ami-id <ami_id>  AMI id [default: ami-fb50968c]
  -c COUNT, --count COUNT         Number of instances to launch [default: 1]
  -z <av_zone>, --zone <av_zone>  Availability zone [default: eu-west-1a]
  -s <sg>, --sec-group <sg>       Security group
  -S <subnet>, --subnet <subnet>  Subnet ID

"""

import sys
from   pprint import pprint

from   docopt import  docopt

import boto
import boto.regioninfo
import boto.ec2

###############################################################################

def get_status(c = None, rids = [], filters = {}):
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

if options['verbose']:
  print "Region: %s" % options['region']

conn = boto.ec2.connect_to_region(options['region'])

if conn is None:
  print "Could not connect to region %s" % options['region']
  sys.exit(1)

if options['status']:
  get_status(conn)

if options['request']:
  request_instance(conn, options)

