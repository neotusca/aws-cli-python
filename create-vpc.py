#!/usr/bin/python

import os
import sys
import subprocess
import json

VPC_NET='172.33.0.0/16'
SUBNET=[]
SUBNET.append('172.33.0.0/24')
SUBNET.append('172.33.1.0/24')
SUBNET.append('172.33.2.0/24')
SUBNET.append('172.33.3.0/24')
SUBNET.append('172.33.4.0/24')
SUBNET.append('172.33.5.0/24')
AZ=['ap-northeast-2a','ap-northeast-2c']


def main():
    VPC_ID = create_vpc(VPC_NET)
    #VPC_ID = 'vpc-07840d345b965edb7'
    print("VPC_ID : %s" % VPC_ID)

    SUBNET_IDS = create_subnet(VPC_ID, SUBNET, AZ)
    print("SUBNET_ID : %s" % SUBNET_IDS)

    IGW_ID = create_igw()
    #IGW_ID = 'igw-0f06c122ee36b1d2a'
    print("IGW_ID : %s" % IGW_ID)
    attach_igw(VPC_ID, IGW_ID)

    EIP_ID = allocate_nat_eip()
    #EIP_ID = 'eipalloc-0631cc8b4fff09a88'
    print("EIP_ID : %s" % EIP_ID)

    NGW_ID = create_ngw(EIP_ID, SUBNET_IDS[0])
    #print("NGW_ID : %s" % NGW_ID)

    '''
    VPC_ID = 'vpc-0f0a7902914e87d22'
    SUBNET_IDS = ['subnet-094132a7e8623a033', 'subnet-02c0445125b6f3933', 'subnet-0017a1ad40ba2ac35', 'subnet-05024c52413b6a566', 'subnet-076309362c4cfa424', 'subnet-0540c3a89ad12f535']
    IGW_ID = 'igw-00e20b81d4e5e32d0'
    NGW_ID = 'nat-0480fde96b76e2793'
    '''

    create_routetable(VPC_ID, SUBNET_IDS, IGW_ID, NGW_ID)


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def create_vpc(vpcnet):
    print('### 1. create_vpc')
    lines=''
    cmd_string = 'aws ec2 create-vpc  --cidr-block ' + vpcnet
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        #print(type(line),line)
        lines = lines + line
    dict_1 = json.loads(lines)
    #print(type(dict_1), dict_1)
    vpcid = dict_1['Vpc']['VpcId']
    return vpcid

def create_subnet(vpcid, subnets, az):
    print('### 2. create_subnet')
    i=0
    subnetids=[]
    for subnet_range in subnets:
        #print(subnet_range,'-', az[i%2], '-', vpcid)
        lines=''
        cmd_string = 'aws ec2 create-subnet  --cidr-block ' + subnet_range + '  --availability-zone ' + az[i%2] + '  --vpc-id  ' + vpcid
        print(cmd_string)
        result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        for line in result_1.stdout.readlines():
            #print(type(line),line)
            lines = lines + line
        dict_1 = json.loads(lines)
        #print(type(dict_1), dict_1)
        subnetid = dict_1['Subnet']['SubnetId']
        subnetids.append(subnetid)
        i=i+1
    return subnetids

def create_igw():
    print('### 3. create_internet-gw')
    lines=''
    cmd_string = 'aws ec2 create-internet-gateway'
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        lines = lines + line
    #print(lines)
    dict_1 = json.loads(lines)
    #print(type(dict_1), dict_1)
    igwid = dict_1['InternetGateway']['InternetGatewayId']
    return igwid

def attach_igw(vpcid, igwid):
    print('### 4. attach_internet-gw')
    lines=''
    cmd_string = 'aws ec2 attach-internet-gateway --vpc-id ' + vpcid + ' --internet-gateway-id ' + igwid
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        lines = lines + line
    print(lines)

def allocate_nat_eip():
    print('### 5. allocate_nat_eip')
    lines=''
    cmd_string = 'aws ec2 allocate-address  --network-border-group ap-northeast-2'
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        lines = lines + line
    #print(lines)
    dict_1 = json.loads(lines)
    #print(type(dict_1), dict_1)
    eipid = dict_1['AllocationId']
    return eipid

def create_ngw(eipid, public_subnet):
    print('### 6. create_nat-gw')
    lines=''
    cmd_string = 'aws ec2  create-nat-gateway --subnet-id ' + public_subnet  + ' --allocation-id ' + eipid
    print(cmd_string)
    result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    for line in result_1.stdout.readlines():
        lines = lines + line
    #print(lines)
    dict_1 = json.loads(lines)
    #print(type(dict_1), dict_1)
    ngwid = dict_1['NatGateway']['NatGatewayId']
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
        print(cmd_string)
        result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        for line in result_1.stdout.readlines():
            lines = lines + line
        dict_1 = json.loads(lines)
        print(type(dict_1), dict_1)
        rtid = dict_1['RouteTable']['RouteTableId']
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
            j=j+1
            k=k+1

        print('### 7-3. create-route')
        lines=''
        if i == 0:
            cmd_string = 'aws ec2  create-route   --route-table-id ' + rtid + '  --destination-cidr-block 0.0.0.0/0  --gateway-id  ' + igwid
        else:
            cmd_string = 'aws ec2  create-route   --route-table-id ' + rtid + '  --destination-cidr-block 0.0.0.0/0  --gateway-id  ' + ngwid
        print(cmd_string)
        result_1 = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        for line in result_1.stdout.readlines():
            lines = lines + line
        dict_1 = json.loads(lines)
        print(type(dict_1), dict_1)
        i=i+1



if __name__ == "__main__":
    main()
