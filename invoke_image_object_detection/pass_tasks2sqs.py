import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.us-west-2.amazonaws.com/230755935769/a2i-tasks'


def send2sqs(a2i_id): 

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
            'Information about current NY Times fiction bestseller for '
            'week of 12/11/2016.'
        )
    )
    
    print(response['MessageId'])