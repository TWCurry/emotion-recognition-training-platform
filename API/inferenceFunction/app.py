import sys
import tensorflow as tf

def lambda_handler(event, context):
    try:
        body = event["body"]
    except Exception as e:
        print("Could note read body")
        return {
            "statusCode": 400,
            "body": "Invalid request body"
        }
    print(body)
    return {
        "statusCode": 200,
        "body": "Request successful"
    }
