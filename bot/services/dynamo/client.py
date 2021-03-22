import os
import boto3

from boto3.dynamodb.conditions import Key

class DynamoClient:

    def __init__(self, table_name_env_var):
        aws_access_key = os.environ.get("AWS_ACCESS_KEY")
        aws_secret_key = os.environ.get("AWS_SECRET_KEY")
        table_name = os.environ.get(table_name_env_var)

        if not aws_access_key or not aws_secret_key or not table_name:
            raise Exception("Unable to initialize Dynamo client, missing AWS access key, AWS secret key, or table name. Check environmental variables")

        dynamo = boto3.resource(
            'dynamodb',
            'us-east-1',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.client = dynamo.Table(table_name)

    def get_word_frequency(self, author_id, word):
        response = self.client.query(
            KeyConditionExpression=Key('authorId').eq(author_id) & Key('word').eq(word)
        )

        if not response["Items"]:
            return 0
        else:
            return response["Items"][0]["count"]
