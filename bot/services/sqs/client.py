import os
import boto3
import json
import uuid

class SQSClient:

    def __init__(self, queue_url_env_var):
        aws_access_key = os.environ.get("AWS_ACCESS_KEY")
        aws_secret_key = os.environ.get("AWS_SECRET_KEY")
        self.queue_url = os.environ.get(queue_url_env_var)

        if not aws_access_key or not aws_secret_key or not self.queue_url:
            raise Exception("Unable to initialize SQS client, missing AWS access key, AWS secret key, or queue URL. Check environmental variables")

        self.client = boto3.client(
            'sqs',
            'us-east-1',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    def send_message(self, msg):
        r = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(msg)
        )

    def send_fifo_message(self, msg, msg_group_id):
        r = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(msg),
            MessageGroupId=msg_group_id,
            MessageDeduplicationId=str(uuid.uuid4())
        )
