import boto3, base64
from urllib.parse import unquote
# import tensorflow as tf

def lambda_handler(event, context):
    try:
        body = event["body"]
    except Exception as e:
        print("Invalid request body.")
        return {
            "statusCode": 400,
            "body": "Invalid request body."
        }
    print(body)
    body = unquote(body) # Url decode body
    print(body)
    body = base64.b64decode(body)
    print(body)
    f = open("tmp/tmp.jpg", "wb")
    f.write(body)
    f.close()
    # s3 = boto3.resource('s3')
    # object = s3.Object('tc-emotion-recognition-models', 'test.jpg')
    # object.put(Body=body)
    return {
        "statusCode": 200,
        "body": "Request successful"
    }