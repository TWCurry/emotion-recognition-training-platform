import boto3, base64, cv2, os, json
import numpy as np
import flask
from flask import Flask, request
from urllib.parse import unquote
import tflite_runtime.interpreter as tflite

# Initialisation
app = Flask(__name__)

@app.route("/uploadImage", methods=["POST"])
def infer():
    # Load Config
    try:
        f = open("config.json", "r")
        configData = json.loads(f.read())
        f.close()
        modelPath = configData["modelPath"]
        modelBucket = configData["modelBucket"]
    except Exception as e:
        print(f"Could not load config - {e}")
        return createResponse(500, f"Could not load config - {e}")

    # print(request.form[0])
    imageData = str(request.form.getlist('imageData')[0])
    print("Loading image...")
    imageData = unquote(imageData) # Url decode body
    imageData = imageData.split(",")[1] # Remove b64 header
    imageData = base64.b64decode(imageData) # decode base64 to bytes
    nparr = np.fromstring(imageData, np.uint8) # Load image into numpy array
    img = cv2.imdecode(nparr, 0) # Convert to grayscale cv2 image

    # Load Haar-Cascade
    print("Loading Haar-Cascade...")
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Detect the faces in the image
    print("Detecting faces in image...")
    faces = faceCascade.detectMultiScale(img, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Download model from S3
    print("Downloading model from S3...")
    try:
        s3 = boto3.client('s3')
        s3.download_file(modelBucket, modelPath, "model.tflite")
    except Exception as e:
        print(f"Could not load model - {e}")
        return createResponse(500, f"Could not load model - {e}")

    # Load model
    interpreter = tflite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Successfully loaded model.")

    response = flask.jsonify({"body": "Success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def createResponse(statusCode, body):
    # Simple function to generate HTTP response with correct headers (to reduce repeated code)
    return flask.jsonify({
        "statusCode": statusCode,
        "body": str(body)
    })

if __name__ == "__main__":
    app.run()