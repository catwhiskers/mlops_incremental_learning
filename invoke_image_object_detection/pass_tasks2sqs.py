import boto3

# Create SQS client
sqs = boto3.client('sqs')

def send2sqs(a2i_id, queue_url): 
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'a2i-task-id': {
                'DataType': 'String',
                'StringValue': a2i_id
            }
        },
        MessageBody=(
            'send to sqs'
        )
    )
    
    print(response['MessageId'])
