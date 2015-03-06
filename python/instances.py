#!/usr/bin/env python
"""Usage: 
  instances start [options]
  instances -h|--help
  
Generic options:

  -h, --help                          This help
  -v, --verbose                       Make the output verbose
  -d, --debug                         Debug information
  -n, --dry-run                       Simulate
  -r <region>, --region <region>      Region name [default: us-east-1]
  --profile <profile_name>            Boto profile name [default: Credentials]

Start options:
  -a <ami_id>, --ami-id <ami_id>      AMI id [default: ami-fb50968c]
  -t <type>, --type <type>            Instance type [default: t1.micro]
  -s <sg>, --sec-group <sg>           Security groups
  -k <name>, --key <key_name>         Identity key name [default: ]
  -c COUNT, --count COUNT             Number of instances to launch [default: 1]
  -z <av_zone>, --zone <av_zone>      Availability zone
  -S <subnet>, --subnet <subnet>      Subnet ID
  -T <tags>, --tags <tags>            Key1:Value1[,Key2:value2...] [default: Name:new-instance]

"""

import sys
import time
from   pprint import pprint

from   docopt import  docopt

import boto
import boto.regioninfo
import boto.ec2

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
      nfo = boto.ec2.instanceinfo.InstanceInfo(c, i.instance_id)
      pprint(dir(nfo))


def run_instances(c = None, o = None):
  if c is None:
    return false

  #  security_group_ids = o['sec-group'],
  reservation = c.run_instances(
    o['ami-id'],
    instance_type      = o['type'],
    placement       = o['zone'],
    subnet_id          = o['subnet'],
    key_name           = o['key'],
    min_count          = o['count'],
    max_count          = o['count'],
  )

  print reservation
  
  tags = dict([ i.split(':') for i in o['tags'].split(',') ])
    
  pending = []
  # Tag instances
  for instance in reservation.instances:
    status = instance.update()

    if status == 'pending':
      pending.append(instance)
      continue

    instance.add_tags(tags)

  time.sleep(30)

  # Retry pending
  if len(pending) > 0:
    for instance in pending:
      status = instance.update()
      if status == 'pending':
        #pending2.append(instance)
        print dir(instance)
        continue
      instance.add_tags(tags)

  
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

region = boto.ec2.get_region(options['region'])
#conn   = boto.ec2.EC2Connection(region = region, profile_name = options['profile'])
#conn   = boto.connect_ec2(region = region, profile_name = options['profile'])
conn   = boto.connect_ec2(region = region)

if conn is None:
  print "Could not connect to region %s" % options['region']
  sys.exit(1)

if options['start']:
  run_instances(conn, options)

