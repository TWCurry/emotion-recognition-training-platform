import boto3, base64, cv2
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
    body = unquote(body) # Url decode body
    body = base64.b64decode(body)
    f = open("tmp/tmp.jpg", "wb")
    f.write(body)
    f.close()
    img = cv2.imread("tmp/tmp.jpg", 0)
    # s3 = boto3.resource('s3')
    # object = s3.Object('tc-emotion-recognition-models', 'test.jpg')
    # object.put(Body=body)
    return {
        "statusCode": 200,
        "body": "Request successful"
    }