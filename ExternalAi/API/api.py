import flask, random, base64, cv2, sys
from flask import Flask
from flask import Flask, request
from google.cloud import storage
from urllib.parse import unquote
import numpy as np
import tflite_runtime.interpreter as tflite

# Initialisation
classNames = ['11214', '18651', '2357', '3003', '3004', '3005', '3022', '3023', '3024', '3040', '3069', '32123', '3673', '3713', '3794', '6632']
app = Flask(__name__)
client = storage.Client()
bucketName = "tc-fer-application-datasets"
folderPrefix="legoDataset"
bucket = client.bucket(bucketName)

@app.route("/fetchImages", methods=["GET"])
def fetchImages():
    imgNames = []
    returnData = {}
    for blob in client.list_blobs(bucketName, prefix="legoDataset"):
        imgNames.append(blob)
    for i in range(9):
        index = random.randint(0, len(imgNames)-1)
        blob = bucket.blob(imgNames[index].name)
        data = blob.download_as_bytes()
        b64Data = base64.b64encode(data)
        returnData[i] = {imgNames[index].name:(str(b64Data))}

    response = flask.jsonify({
        "statusCode": 200,
        "body": returnData
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/identifyBrickType", methods=["POST"])
def identifyBrickType():
    imageNames = str(request.args.get('imageNames'))
    typeToIdentify = str(request.args.get('typeToIdentify'))
    indicesContainingImage = []
    for i in range(len(imageNames)-1):
        blob = bucket.blob(imageNames[i])
        data = blob.download_as_bytes()
        npArr = np.frombuffer(data, np.uint8) # Load image into numpy array
        imgArr = np.zeros((200, 200)) # Empty array, will store the image data

        # Load Haar-Cascade
        print("Loading Haar-Cascade...")
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Detect the faces in the image
        print("Detecting faces in image...")
        faces = faceCascade.detectMultiScale(npArr, 1.1, 4)
        if(len(faces)) == 0:
            response = flask.jsonify({
                "statusCode": 200,
                "body": "No faces found."
            })
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        
        # Load model
        print("Loading model...")
        interpreter = tflite.Interpreter(model_path="model.tflite")
        interpreter.allocate_tensors()

        # Load input data to model
        inputDetails = interpreter.get_input_details()
        outputDetails = interpreter.get_output_details()
        inputData = np.expand_dims(imgArr, axis=3)
        interpreter.set_tensor(inputDetails[0]['index'], inputData)
        print("Successfully loaded model, running...")

        # Run model
        interpreter.invoke()
        predictions = interpreter.get_tensor(outputDetails[0]['index'])
        classType = classNames[np.argmax(predictions[0])]

        # If current image contains chosen brick type:
        if classType == typeToIdentify:
            indicesContainingImage.append(i)

if __name__ == "__main__":
    app.run()