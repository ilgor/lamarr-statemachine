from datetime import datetime
from uuid import uuid4
import boto3
import time


table_name = 'LamarrTracking'

def find_instance_by_name(ec2, name):
    tags = ec2.describe_tags()['Tags']
    for tag in tags:
        if tag['Key'] == 'Name' and tag['Value'] == 'lab1':
            return ec2
    return None

def lambda_handler(event, context):    
    ec2 = _get('arn:aws:iam::405696771294:role/hopper-ec2', f'arn:aws:iam::624041382079:role/allow-assume-EC2-role-in-Lamarr1', 'ec2')
    instance = find_instance_by_name(ec2, "lab1")
    print('BAHA: ', instance)
    _create_table()
    time.sleep(10)
    _put_data(instance)


def _create_table():
    client = boto3.client('dynamodb')
    
    existing_tables = client.list_tables()['TableNames']

    if table_name not in existing_tables:
        response = client.create_table(
            TableName = table_name,
            AttributeDefinitions=[
                {
                    "AttributeName": "sg_id",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "sg_group_name",
                    "AttributeType": "S"
                }
            ],
            KeySchema=[
                {
                    "AttributeName": "sg_id",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "sg_group_name",
                    "KeyType": "RANGE"
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )


def _put_data(instance):
    print("ILGOR: ", instance.describe_security_groups()['SecurityGroups'])
    client = boto3.client('dynamodb')
    response = client.put_item(
        TableName = table_name, 
        Item = {
            'instance_id': {'S':str(uuid4())},
            'sg_id': {'S': str(instance.describe_security_groups()['SecurityGroups']['Id'])},
            'sg_group_name': {'S': instance.describe_security_groups()['SecurityGroups']['SecurityGroupName']},
            'time_stamp': {'S': str(datetime.now())}
        }
    )
    return response


def _get(hopper_role_arn, lamarr_role_arn, service):
    client_hopper = boto3.client('sts')
    response = client_hopper.assume_role(RoleArn=hopper_role_arn, RoleSessionName='assuming-hopper')
    credentials = response['Credentials']

    client_lamarr = boto3.client(
        'sts',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    response_lamarr = client_lamarr.assume_role(RoleArn=lamarr_role_arn, RoleSessionName='assuming-lamarr')
    credentials_hopper = response_lamarr['Credentials']

    return boto3.client(
        service,
        aws_access_key_id=credentials_hopper['AccessKeyId'],
        aws_secret_access_key=credentials_hopper['SecretAccessKey'],
        aws_session_token=credentials_hopper['SessionToken'],
    )