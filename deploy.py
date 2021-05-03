import sagemaker
import boto3 

import argparse
import time
from sagemaker import get_execution_role

# Parse argument variables passed via the DeployModel processing step
parser = argparse.ArgumentParser()
parser.add_argument('--group-name', type=str)
parser.add_argument('--endpoint-name', type=str)
args = parser.parse_args()

timestamp = str(int(time.time())) 
group_name = args.group_name 
endpoint_name = args.endpoint_name 
model_name = "objectdetection-"+ timestamp
endpoint_config_name = "objectdetection-modelconfig-"+ timestamp
role = get_execution_role()



sm_client = boto3.client('sagemaker')

def get_latest_approved_model(group_name): 
    info = sm_client.list_model_packages(ModelPackageGroupName=group_name)
    models = info['ModelPackageSummaryList']
    latest = sorted(models, key=lambda x:x['ModelPackageVersion'])[-1]
    latestarn = latest['ModelPackageArn']
    return latestarn
    


def create_model(group_name, model_name): 
    print("Model name : {}".format(model_name))
    #get it use model registry api 
    model_version_arn = get_latest_approved_model(group_name)
    primary_container = {
        'ModelPackageName': model_version_arn,
    }
    create_model_respose = sm_client.create_model(
        ModelName = model_name,
        ExecutionRoleArn = role,
        PrimaryContainer = primary_container
    )
    print("Model arn : {}".format(create_model_respose["ModelArn"]))



def create_endpoint_config(endpoint_config_name, model_name):
    create_endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName = endpoint_config_name,
        ProductionVariants=[{
            'InstanceType':'ml.m5.xlarge',
            'InitialVariantWeight':1,
            'InitialInstanceCount':1,
            'ModelName':model_name,
            'VariantName':'AllTraffic'}])


def update_endpoint(endpoint_name, endpoint_config_name): 
    print("EndpointName={}".format(endpoint_name))

    create_endpoint_response = sm_client.update_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name)
    print(create_endpoint_response['EndpointArn'])
    
create_model(group_name, model_name)    
create_endpoint_config(endpoint_config_name, model_name)
update_endpoint(endpoint_name, endpoint_config_name)

