import boto3
import json
import time


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


def lambda_handler(event, context):
    ec2 = _get('arn:aws:iam::405696771294:role/hopper-ec2', f'arn:aws:iam::{event["account"]["account-number"]}:role/allow-assume-EC2-role-in-Lamarr1', 'ec2')
    try:
        ec2.describe_key_pairs(KeyNames=['DemoKey', ],)
    except Exception as e:
        keypair = ec2.create_key_pair(KeyName='DemoKey')

    cf = _get('arn:aws:iam::405696771294:role/hopper-cf', f'arn:aws:iam::{event["account"]["account-number"]}:role/allow-assume-CF-role-in-Lamarr', 'cloudformation')
    try:
        r1 = cf.describe_stacks(StackName='InitialSetup')['Stacks'][0]
        r2 = cf.delete_stack(StackName='InitialSetup')['ResponseMetadata']['HTTPStatusCode']
        time.sleep(5)
        print(f'Stack Deletion Status: {r2}')
    except Exception as e:
        pass

    la_create_stack_parameters = []
    la_create_stack_parameters.append({"ParameterKey": "KeyName", "ParameterValue": "DemoKey"})
    la_create_stack_parameters.append({"ParameterKey": "InstanceType", "ParameterValue": "t2.micro"})

    stack_result = {}

    try:
        stack_result = cf.create_stack(
            StackName=event["StackName"], 
            DisableRollback=True, 
            TemplateURL=event["TemplateUrl"], 
            Parameters=la_create_stack_parameters, 
            Capabilities=["CAPABILITY_IAM"])
    except Exception as e:
        print(e)
    return stack_result