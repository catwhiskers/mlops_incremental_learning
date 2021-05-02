import os
import io
import boto3
import json
import csv
import base64
import subprocess
import sys 
import uuid 

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
A2IFLOW_DEF = os.environ['A2IFLOW_DEF']
BUCKET = os.environ['BUCKET']
KEY = os.environ['KEY']
SQS_URL = os.environ['SQS_URL']

runtime= boto3.client('runtime.sagemaker')
s3_client = boto3.client('s3')
a2i = boto3.client('sagemaker-a2i-runtime')

def object_with_max_prob(dets):
    dets = dets["prediction"]
    dets = sorted(dets, key = lambda x:x[1], reverse=True)
    return dets[0]  


def lambda_handler(event, context):
    body = event["content"]
    payload = base64.b64decode(body)
    runtime_client = boto3.client('runtime.sagemaker')
    response = runtime_client.invoke_endpoint(EndpointName=ENDPOINT_NAME, 
                                  ContentType='application/x-image', 
                                  Body=payload)
    
    result = response['Body'].read().decode('utf-8')
    obj = object_with_max_prob(json.loads(result))
    
    if obj[1] < 1: 
        task = str(uuid.uuid4())
        file_name = "{}.jpg".format(task) 
                    
        s3_client.put_object(Body=payload, Bucket=BUCKET, Key="{}/{}".format(KEY,file_name))
        s3_filename = "s3://{}/{}/{}".format(BUCKET, KEY, file_name)                    
        inputContent = {
            "initialValue": obj[0],
            "taskObject": s3_filename # the s3 object will be passed to the worker task UI to render
        }
        # start an a2i human review loop with an input
        flowDefinitionArn = A2IFLOW_DEF                   
    
        start_loop_response = a2i.start_human_loop(
            HumanLoopName=task,
            FlowDefinitionArn=flowDefinitionArn,
            HumanLoopInput={
                "InputContent": json.dumps(inputContent)
            }
        )
        
        # https://forums.aws.amazon.com/thread.jspa?messageID=961211&tstart=0
        
        a2i_arn = start_loop_response['HumanLoopArn'].split('/')[-1]
        
        import pass_tasks2sqs
        pass_tasks2sqs.send2sqs(a2i_arn,SQS_URL)

    
    
    
    return result 