import boto3, base64, cv2, os
from botocore import model
import numpy as np
from urllib.parse import unquote

def lambda_handler(event, context):
    try:
        modelPath = os.environ["modelPath"]
        modelBucket = os.environ["modelBucket"]
    except Exception as e:
        print("Missing environment variables.")
        return response(500, "Missing environment variables.")
    try:
        body = event["body"]
    except Exception as e:
        print("Invalid request body.")
        return response(400, "Invalid request body.")

    body = unquote(body) # Url decode body
    body = body.split(",")[1] # Remove b64 header
    body = base64.b64decode(body) # decode base64 to bytes
    nparr = np.fromstring(body, np.uint8) # Load image into numpy array
    img = cv2.imdecode(nparr, 0) # Convert to grayscale cv2 image

    # Load Haar-Cascade
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Detect the faces in the image
    faces = faceCascade.detectMultiScale(img, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Load model from S3
    s3 = boto3.resource('s3')
    s3Object = s3.get_object(Bucket=modelBucket, Key=modelPath)
    body = s3Object["Body"]

    # For testing, write as jpeg, then read and upload to s3
    # cv2.imwrite("/tmp/tmp.jpg", img)
    # f = open("/tmp/tmp.jpg", "rb")
    # data = f.read()
    # f.close()

    # object = s3.Object('tc-emotion-recognition-models', 'test.jpg')
    # object.put(Body=data)

    return response(200, "Request successful")

def response(statusCode, body):
    # Simple function to generate HTTP response with correct headers (to reduce repeated code)
    return {
        "statusCode": statusCode,
        "headers": {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : True
        },
        "body": str(body)
    }
