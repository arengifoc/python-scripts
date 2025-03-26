#!/usr/bin/env python3
"""
Script that lists EC2 instances in an AWS account
"""
import argparse
from typing import Any
import boto3
import botocore


def list_ec2_instances(session: boto3.session.Session, filters: dict) -> list[dict[str, Any]]:
    """
    Lists EC2 instances in an AWS account

    Args:
        session (boto3.session.Session): AWS session
    Returns:
        list[dict[str,Any]]: A list of dictionaries with EC2 instances attributes.
    """
    ec2_instances = []
    client = session.client('ec2')
    instances = client.describe_instances(Filters=filters)
    if len(instances['Reservations']) == 0:
        return ec2_instances
    for instance in instances['Reservations']:
        instance_id = instance['Instances'][0]['InstanceId']
        dns_name = instance['Instances'][0]['PrivateDnsName']
        state = instance['Instances'][0]['State']['Name']
        platform = instance['Instances'][0].get('Platform', 'linux')
        instance_type = instance['Instances'][0]['InstanceType']
        if state != 'terminated':
            ip = instance['Instances'][0]['PrivateIpAddress']
        else:
            ip = 'N/A'
        name = next((tag['Value'] for tag in instance['Instances']
                     [0]['Tags'] if tag['Key'] == 'Name'), 'NoName')
        ec2_instances.append({'instance_id': instance_id, 'name': name,
                              'ip': ip, 'state': state, 'dns_name': dns_name,
                              'platform': platform,
                              'instance_type': instance_type})
    return ec2_instances


def print_ec2_instances(ec2_instances: list[dict[str, Any]]) -> None:
    """
    Prints EC2 instances in a table format
    
    Args:
        ec2_instances (list[dict[str, Any]]): List of EC2 instances attributes
    Returns:
        None
    """
    if len(ec2_instances) == 0:
        print('No EC2 instances found')
        return
    name_max_width = max(len(x['name']) for x in ec2_instances)
    ip_max_width = max(len(x['ip']) for x in ec2_instances)
    state_max_width = max(len(x['state']) for x in ec2_instances)
    dns_name_max_width = max(len(x['dns_name']) for x in ec2_instances)
    platform_max_width = max(len(x['platform']) for x in ec2_instances)
    instance_type_max_width = max(
        len(x['instance_type']) for x in ec2_instances)
    print(f'{"Name":<{name_max_width}}  ' +
          f'{"Instance ID":<19}  ' +
          f'{"IP":<{ip_max_width}}  ' +
          f'{"Platform":<{platform_max_width}}  ' +
          f'{"Instance Type":<{instance_type_max_width}}  ' +
          f'{"State":<{state_max_width}}  ' +
          f'{"DNS Name":<{dns_name_max_width}}'
          )
    print('-'*name_max_width + '  ' +
          '-'*19 + '  ' +
          '-'*ip_max_width + '  ' +
          '-'*platform_max_width + '  ' +
          '-'*instance_type_max_width + '  ' +
          '-'*state_max_width + '  ' +
          '-'*dns_name_max_width)
    for instance in ec2_instances:
        print(f'{instance["name"]:<{name_max_width}}  ' +
              f'{instance["instance_id"]:<19}  ' +
              f'{instance["ip"]:<{ip_max_width}}  ' +
              f'{instance["platform"]:<{platform_max_width}}  ' +
              f'{instance["instance_type"]:<{instance_type_max_width}}  ' +
              f'{instance["state"]:<{state_max_width}}  ' +
              f'{instance["dns_name"]:<{dns_name_max_width}}'
              )


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments

    Return:
        argparse.Namespace: Arguments parsed
    """
    parser = argparse.ArgumentParser(
        description='List EC2 instances in an AWS account')
    parser.add_argument('-i', '--instance-ids', help='Instance IDs')
    parser.add_argument('-I', '--ip-addresses', help='IP addresses')
    parser.add_argument('-s', '--state', help='State')
    parser.add_argument('-p', '--platform', help='Platform')
    return parser.parse_args()


def main() -> None:
    """
    Main function
    
    Args:
        None
    Returns:
        None
    """
    aws_session = boto3.session.Session()
    args = parse_args()
    ec2_filters = []
    if args.instance_ids:
        ec2_filters.append({'Name': 'instance-id',
                            'Values': args.instance_ids.split(',')})
    if args.ip_addresses:
        ec2_filters.append({'Name': 'private-ip-address',
                            'Values': args.ip_addresses.split(',')})
    if args.state:
        ec2_filters.append({'Name': 'instance-state-name',
                            'Values': args.state.split(',')})
    platform_filter = {}
    if args.platform:
        if args.platform == 'linux':
            platform_filter = {
                'Name': 'platform-details',
                'Values': ['Linux/*']
            }
        elif args.platform == 'mac':
            platform_filter = {
                'Name': 'instance-type',
                'Values': ['mac*']
            }
        else:
            platform_filter = {
                'Name': 'platform',
                'Values': ['windows']
            }
    try:
        ec2_filters.append(platform_filter)
        ec2_data = list_ec2_instances(aws_session, filters=ec2_filters)
        print_ec2_instances(ec2_data)
    except botocore.exceptions.NoCredentialsError as error:
        print(f'Error: {error}')
        print('Please configure your AWS credentials')
        return
    except botocore.exceptions.PartialCredentialsError as error:
        print(f'Error: {error}')
        print('Please configure your AWS credentials')
        return
    except botocore.exceptions.ClientError as error:
        print(f'Error creating AWS session: {error}')
        return
    except botocore.exceptions.EndpointConnectionError as error:
        print(f'Error connecting to AWS endpoint: {error}')
        return
    except botocore.exceptions.BotoCoreError as error:
        print(f'General BotoCore error: {error}')
        return


if __name__ == '__main__':
    main()
