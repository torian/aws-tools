#!/usr/bin/env python
"""Usage: elb [-r REGION] [-l LBNAME]

-r REGION, --region REGION  Region name [default: eu-west-1]
-l LBNAME, --lb LBNAME      Load Balancer name
"""

from   docopt import  docopt

import boto
import boto.ec2.elb 
import boto.ec2.elb.loadbalancer
import boto.regioninfo

# Options from __doc__
opts = docopt(__doc__)

cfg = {
  'endpoint':    'elasticloadbalancing.amazonaws.com',
  'APIVersion':  '2012-06-01',
}

region = boto.regioninfo.RegionInfo(
  name     = opts['--region'],
  endpoint = '%s.%s' % (opts['--region'], cfg['endpoint'])
  )

print "Boto version: %s" % boto.Version
print region

conn = boto.connect_elb(region = region)

if opts['--lb'] is None:
  lbs = conn.get_all_load_balancers()

  for lb in lbs:
    print lb

else:
  lb_health = conn.describe_instance_health(opts['--lb'])

  #lb_attrs = conn.get_all_lb_attributes(opts['--lb'])
  #for attr in lb_attrs:
  #  print attr

  for node in lb_health:
    print node
