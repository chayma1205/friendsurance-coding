from os import path
import os
import json, boto3, sys, uuid
import requests
import datetime
from datetime import datetime


def handler(event, context):
    bucket_name = os.environ['bucket_name']
    dynamodb_table = os.environ['dynamodb']
    eventBody = json.loads(json.dumps(event))['body']
    url = json.loads(eventBody)['url']
    now = datetime.now()
    time_stamp = now.strftime("%m/%d/%Y, %H:%M:%S")
    reqponse = requests.get(url)
    filename = get_filename(url)
    img = reqponse.content
    path = "s3://" + bucket_name + "/" + filename
    s3_client = boto3.resource("s3")
    s3_client.Bucket(bucket_name).put_object(Key=filename, Body=img)
    add_metadata(dynamodb_table, filename, path, url, time_stamp)

    return {'statusCode': 200, 'body': json.dumps('image added')}


def get_filename(url):
    fragment_removed = url.split("#")[0]
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return ""
    return path.basename(scheme_removed)


def add_metadata(dynamodb_table, name, path, url, time_stamp):
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(TableName=dynamodb_table, Item={'Name': {'S': name}, 'OriginalLink': {'S': url}, 'Path': {'S': path}, 'Timestamp': {'S': time_stamp}})
    return {'statusCode': 200}

