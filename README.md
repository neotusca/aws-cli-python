# aws-cli-python

Personal project for building python script for easy distribution on AWS.

## Requirement
1. aws-cli 2 (Linux)
2. python 2

## Function & description
create-vpc.py
- create vpc (B-class)
- create subnet in vpc (C-class)
- create internet gateway
- create nat gateway (include elastic ip)
- create routing-table
- associate routing-table & subnet & gateway


## Bug
1. Need apply 'Public ipv4 dhcp enable' to public subnet
2. Need apply 'DNS hostname enable' to vpc
