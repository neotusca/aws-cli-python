#!/usr/bin/python

import os
import sys
import subprocess
import json

VPC_NET='172.93.0.0/16'
SUBNET=[]
SUBNET.append('172.93.0.0/24')
SUBNET.append('172.93.1.0/24')
SUBNET.append('172.93.2.0/24')
SUBNET.append('172.93.3.0/24')
SUBNET.append('172.93.4.0/24')
SUBNET.append('172.93.5.0/24')
AZ=['ap-northeast-2a','ap-northeast-2c']


def main():
    VPC_ID = create_vpc(VPC_NET)
    print("VPC_ID : %s" % VPC_ID)

    SUBNET_IDS = create_subnet(VPC_ID, SUBNET, AZ)
    print("SUBNET_ID : %s" % SUBNET_IDS)

    IGW_ID = create_igw()
    print("IGW_ID : %s" % IGW_ID)
    attach_igw(VPC_ID, IGW_ID)

    EIP_ID = allocate_nat_eip()
    print("EIP_ID : %s" % EIP_ID)

    NGW_ID = create_ngw(EIP_ID, SUBNET_IDS[0])
    print("NGW_ID : %s" % NGW_ID)

    create_routetable(VPC_ID, SUBNET_IDS, IGW_ID, NGW_ID)


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def cmd_execute(cmd):
    print(cmd)
    result_1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    lines=''
    for line in result_1.stdout.readlines():
        print(type(line),line)
        lines = lines + line
    dict_1 = json.loads(lines)
    return dict_1

def create_vpc(vpcnet):
    print('### 1. create_vpc')
    cmd_string = 'aws ec2 create-vpc  --cidr-block ' + vpcnet
    json_str = cmd_execute(cmd_string)
    vpcid = json_str['Vpc']['VpcId']
    return vpcid

def create_subnet(vpcid, subnets, az):
    print('### 2. create_subnet')
    i=0
    subnetids=[]
    for subnet_range in subnets:
        cmd_string = 'aws ec2 create-subnet  --cidr-block ' + subnet_range + '  --availability-zone ' + az[i%2] + '  --vpc-id  ' + vpcid
        json_str = cmd_execute(cmd_string)
        subnetid = json_str['Subnet']['SubnetId']
        subnetids.append(subnetid)
        i=i+1
    return subnetids

def create_igw():
    print('### 3. create_internet-gw')
    cmd_string = 'aws ec2 create-internet-gateway'
    json_str = cmd_execute(cmd_string)
    igwid = json_str['InternetGateway']['InternetGatewayId']
    return igwid

def attach_igw(vpcid, igwid):
    print('### 4. attach_internet-gw')
    cmd_string = 'aws ec2 attach-internet-gateway --vpc-id ' + vpcid + ' --internet-gateway-id ' + igwid
    lines=''
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        lines = lines + line
    print(lines)


def allocate_nat_eip():
    print('### 5. allocate_nat_eip')
    cmd_string = 'aws ec2 allocate-address  --network-border-group ap-northeast-2'
    json_str = cmd_execute(cmd_string)
    eipid = json_str['AllocationId']
    return eipid

def create_ngw(eipid, public_subnet):
    print('### 6. create_nat-gw')
    cmd_string = 'aws ec2  create-nat-gateway --subnet-id ' + public_subnet  + ' --allocation-id ' + eipid
    json_str = cmd_execute(cmd_string)
    ngwid = json_str['NatGateway']['NatGatewayId']
    return ngwid

def create_routetable(vpcid, subnetids, igwid, ngwid):
    print('### 7. create_routetable')
    print(vpcid, subnetids, igwid, ngwid)
    count = len(subnetids)/2
    i=0
    k=0

    while i < count:
        print('### 7-1. create-route-table')
        lines=''
        cmd_string = 'aws ec2  create-route-table --vpc-id ' + vpcid
        json_str = cmd_execute(cmd_string)
        rtid = json_str['RouteTable']['RouteTableId']
        print(rtid)

        j=0
        while j < 2:
            print('### 7-2. associate-route-table')
            lines=''
            cmd_string = 'aws ec2  associate-route-table --route-table-id  ' + rtid + '  --subnet-id  ' + subnetids[k]
            print(cmd_string)
            result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
            for line in result_1.stdout.readlines():
                lines = lines + line
            print(lines)
            j=j+1
            k=k+1

        print('### 7-3. create-route')
        if i == 0:
            cmd_string = 'aws ec2  create-route   --route-table-id ' + rtid + '  --destination-cidr-block 0.0.0.0/0  --gateway-id  ' + igwid
        else:
            cmd_string = 'aws ec2  create-route   --route-table-id ' + rtid + '  --destination-cidr-block 0.0.0.0/0  --gateway-id  ' + ngwid

        json_str = cmd_execute(cmd_string)
        print(json_str)
        i=i+1

if __name__ == "__main__":
    main()
