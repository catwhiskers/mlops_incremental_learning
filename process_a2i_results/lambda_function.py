import json
import boto3 
from model import get_latest_model_path
from datetime import datetime
import re
import os
from prepare_data import convert_a2i_to_augmented_manifest

BUCKET = os.environ['BUCKET']
PIPELINE = os.environ['PIPELINE']
MODEL_GROUP = os.environ['MODEL_GROUP']


body = "body"
detail = "detail"
humanLoopName = "humanLoopName"
s3_path = "s3-image-path"
loop_status = "HumanLoopStatus"
string_value = "stringValue"


a2i = boto3.client('sagemaker-a2i-runtime')
sm_client = boto3.client('sagemaker')
s3_client = boto3.client('s3')

   
def lambda_handler(event, context):
    completed_human_loops = []  
    # TODO implement
    print(event)
    records = event['Records']
    for record in records: 
        if body in record: 
            bodyjson = json.loads(record[body]) 
            if detail in bodyjson:
                resp = a2i.describe_human_loop(HumanLoopName=bodyjson[detail][humanLoopName])
                if resp[loop_status] == "Completed":
                    completed_human_loops.append(resp)
                    
    if len(completed_human_loops)>0:
    
        output=[]
        training_file = 'augmented.manifest'
        path = "/tmp/{}".format(training_file)
        
        with open(path, 'w') as outfile:
            # convert the a2i json to augmented manifest for each human loop output
            for resp in completed_human_loops:
                splitted_string = re.split('s3://' +  BUCKET + '/', resp['HumanLoopOutput']['OutputS3Uri'])
                output_bucket_key = splitted_string[1]
        
                response = s3_client.get_object(Bucket=BUCKET, Key=output_bucket_key)
                content = response["Body"].read()
                json_output = json.loads(content)
                
                # convert using the function
                augmented_manifest = convert_a2i_to_augmented_manifest(json_output)
                print(json.dumps(augmented_manifest))
                json.dump(augmented_manifest, outfile)
                outfile.write('\n')
                output.append(augmented_manifest)
                print('\n')                    
        
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        key = "a2i-result/{}/{}".format(str(timestamp), training_file)
        
        s3_client.upload_file(path, Bucket=BUCKET, Key=key)                
        s3_path = "s3://{}/{}".format(BUCKET, key)
        last_model_path = get_latest_model_path(MODEL_GROUP) 
        parameters = [
            {
                'Name':'TrainData',
                'Value': s3_path
            },
    
            {
                'Name':'ValidationData',
                'Value': s3_path
            },
    
            {
                'Name':'ModelData',
                'Value': last_model_path
            },
    
        ]
    
        response = sm_client.start_pipeline_execution( PipelineName = PIPELINE, PipelineParameters=parameters)
    
    return {
        'statusCode': 200,
        'body': 'finished'
    }
