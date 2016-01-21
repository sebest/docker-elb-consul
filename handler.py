#!/usr/bin/env python

import os
import sys
import json
import time
import boto.ec2.elb
from subprocess import check_output, CalledProcessError

AWS_REGION = os.environ['AWS_REGION']
ELB_NAME = os.environ['ELB_NAME']

ELB = boto.ec2.elb.connect_to_region(region_name=AWS_REGION)


def elb_register(instances):
    ELB.register_instances(ELB_NAME, instances)

    
def elb_deregister(instances):
    ELB.deregister_instances(ELB_NAME, instances)

    
def elb_instances():
    ELB.describe_instance_health(ELB_NAME)
    
def aws(cmd):
    while True:
        try:
            output = check_output('aws --region %s %s' % (AWS_REGION, cmd), shell=True)
            return json.loads(output)
        except CalledProcessError:
            time.sleep(5)
            continue


def get_instance_id(ip):
    cmd = 'ec2 describe-instances --filter Name=private-ip-address,Values=%s' % (ip)
    data = aws(cmd)
    try:
        return data['Reservations'][0]['Instances'][0]['InstanceId']
    except (KeyError, IndexError):
        print '%s not found in %s' % (ip, AWS_REGION)
        return None


def update_elb(register, deregister):
    cmd = "elb describe-load-balancers --load-balancer-name %s" % (ELB_NAME)
    data = aws(cmd)
    instances = set([i["InstanceId"] for i in data["LoadBalancerDescriptions"][0]["Instances"]])
    print "Instances in %s: %s" % (ELB_NAME, list(instances))

    register -= instances
    if register:
        cmd = 'elb register-instances-with-load-balancer --load-balancer-name %s --instances %s' % (ELB_NAME, ' '.join(register))
        data = aws(cmd)
        instances = set([i['InstanceId'] for i in data["Instances"]])
        print "Instances in %s: %s" % (ELB_NAME, list(instances))
        
    deregister = deregister.intersection(instances)
    if deregister:
        cmd = 'elb deregister-instances-from-load-balancer --load-balancer-name %s --instances %s' % (ELB_NAME, ' '.join(deregister))
        data = aws(cmd)
        instances = set([i['InstanceId'] for i in data["Instances"]])
        print "Instances in %s: %s" % (ELB_NAME, list(instances))

        
def process_update():
    for update in sys.stdin:
        register = set()
        deregister = set()
        for node in json.loads(update):
            ip = node['Node']['Address']
            instance_id = get_instance_id(ip)
            if not instance_id:
                continue
            ok = all([check['Status'] == 'passing' for check in node['Checks']])
            if ok:
                register.add(instance_id)
            else:
                deregister.add(instance_id)
        update_elb(register, deregister)
            
if __name__ == "__main__":
    try:
        check_output('aws iam get-user', shell=True)
    except CalledProcessError as e:
        print "Check your AWS credentials: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        sys.exit(1)
    process_update()
