import flask, random, base64
from flask import Flask
from google.cloud import storage
# Initialisation
app = Flask(__name__)
@app.route("/fetchImages", methods=["GET"])
def fetchImages():
    client = storage.Client()
    bucketName = "tc-fer-application-datasets"
    imgNames = []
    returnData = []
    bucket = client.bucket(bucketName)
    for blob in client.list_blobs(bucketName, prefix="legoDataset"):
        imgNames.append(blob)
    for i in range(9):
        index = random.randint(0, len(imgNames)-1)
        blob = bucket.blob(imgNames[index].name)
        data = blob.download_as_bytes()
        b64Data = base64.b64encode(data)
        returnData.append(b64Data)
    return createResponse(200, returnData)

def createResponse(statusCode, body):
    # Simple function to generate HTTP response with correct headers (to reduce repeated code)
    response = flask.jsonify({
        "statusCode": statusCode,
        "body": str(body)
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    app.run()