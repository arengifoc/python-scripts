## Purpose
A personal utility to list EC2 instances in a friendly format to avoid using `aws ec2 describe-instances`

I made this script just for testing the `boto3` module.


## Usage

```
usage: list_ec2_instances.py [-h] [-i INSTANCE_IDS] [-I IP_ADDRESSES] [-s STATE] [-p PLATFORM]

List EC2 instances in an AWS account

options:
  -h, --help            show this help message and exit
  -i INSTANCE_IDS, --instance-ids INSTANCE_IDS
                        Instance IDs
  -I IP_ADDRESSES, --ip-addresses IP_ADDRESSES
                        IP addresses
  -s STATE, --state STATE
                        State
  -p PLATFORM, --platform PLATFORM
                        Platform
```

## Examples

List all EC2 instances

```bash
export AWS_PROFILE=my-custom-profile
./list_ec2_instances.py
```


List running EC2 instances

```bash
export AWS_DEFAULT_REGION=us-west-2
./list_ec2_instances.py -s running
```

List linux running EC2 instances

```bash
./list_ec2_instances.py -s running -p linux
```
