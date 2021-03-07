import base64, cv2, json, flask, time
import numpy as np
# from PIL import Image
from flask import Flask, request
from urllib.parse import unquote
from google.cloud import firestore
from elasticsearch import Elasticsearch
import tflite_runtime.interpreter as tflite

es = Elasticsearch(["http://35.190.172.118:9200/"])
emotionNames = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"]

# Initialisation
app = Flask(__name__)

@app.route("/uploadImage", methods=["POST"])
def infer():
    if "imageData" in request.args:
        imageData = str(request.form.getlist('imageData')[0])
    else:
        print("Missing imageData")
        response = flask.jsonify({"body": "Missing imageData."})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    print("Loading image...")
    try:
        imageData = unquote(imageData) # Url decode body
        imageData = imageData.split(",")[1] # Remove b64 header
        imageData = base64.b64decode(imageData) # decode base64 to bytes
        nparr = np.frombuffer(imageData, np.uint8) # Load image into numpy array
        img = cv2.imdecode(nparr, 0) # Convert to grayscale cv2 image
    except Exception as e:
        print(f"Image data error - {e}")
        response = flask.jsonify({"body": f"Image data error - {e}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    imgArr = np.zeros((48,48)) # Empty array, will store the image data

    # Load Haar-Cascade
    try:
        print("Loading Haar-Cascade...")
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Detect the faces in the image
        print("Detecting faces in image...")
        faces = faceCascade.detectMultiScale(img, 1.1, 4)
    except Exception as e:
        print(f"Could not load Haar-Cascade - {e}")
        response = flask.jsonify({"body": f"Error identifying faces in image"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    if(len(faces)) == 0:
        print("No faces found.")
        response = flask.jsonify({"body": "No faces found"})
        return response, 200

    for (x, y, w, h) in faces:
        # Capture image of face, resize to 48x48
        faceImage = img[y:y+w,x:x+h]
        faceImage = cv2.resize(faceImage,(48,48))
        # Convert to numpy array and expand dimensions to be used as inputs for models
        imgArr = np.array(faceImage, dtype=np.float32)
        imgArr = np.expand_dims(imgArr, axis=0)

    try:
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
        emotion = emotionNames[np.argmax(predictions[0])]
        print(emotion)
    except Exception as e:
        print(f"Emotion recognition error - {e}")
        response = flask.jsonify({"body": f"Error identifying emotion"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    response = flask.jsonify({
        "statusCode": 200,
        "body": "FER successful",
        "emotion": emotion
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@app.route("/uploadTrainingDetails", methods=["POST"])
def storeTrainingData():
    # Parameters
    requiredParameters = ["modelName", "imageNames", "typeToIdentify", "responseIndex", "emotion"]
    for rParam in requiredParameters:
        if not(rParam in request.args):
            print(f"Missing param '{rParam}'")
            response = flask.jsonify({"body": f"Missing param '{rParam}'"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400
    try:
        modelName = str(request.form.getlist('modelName')[0])
        imageNames = json.loads(request.form.getlist('imageNames')[0])
        typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
        responseIndex = str(request.form.getlist('responseIndex')[0])
        emotion = str(request.form.getlist('emotion')[0])
    except Exception as e:
        print(f"Failed to get parameters - {e}")
        response = flask.jsonify({"body": "Invalid parameters"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    
    if not(emotion in emotionNames):
        print(f"Invalid emotion {emotion}")
        response = flask.jsonify({"body": f"Invalid emotion {emotion}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    
    if len(imageNames != 2):
        print(f"Incorrect number of image names")
        response = flask.jsonify({"body": f"Invalid number of image names ({len(imageNames)} found, should be 2)"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    
    # Check that the response is a valid integer
    try:
        responseIndex = int(responseIndex)
        if responseIndex > 0 or responseIndex > 1:
            print(f"Invalid response index")
            response = flask.jsonify({"body": f"Invalid response index {responseIndex}"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400
    except:
        print(f"Invalid response index datatype")
        response = flask.jsonify({"body": f"Invalid response index datatype"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    responseIndex = str(responseIndex)

    try:
        # Instantiate Firebase connection
        db = firestore.Client()

        # Create string to format image names for DB write
        imageNameStr = ""
        for image in imageNames:
            imageNameStr += image+","
        imageNameStr = imageNameStr[:-1]

        # Write training data to DB
        timestamp = int(time.time())
        document = db.collection("inferenceData").document(f"{timestamp}")
        doc = {
            "modelName": modelName,
            "imageNames": imageNameStr,
            "typeToIdentify": typeToIdentify,
            "responseIndex": responseIndex,
            "emotion": emotion
        }
        # Write to Firestore
        document.set(doc)
    except Exception as e:
        print(f"Could not write to Firestore - {e}")
        response = flask.jsonify({"body": f"Error storing training details"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    try:
        # Write to Elasticsearch
        res = es.index(index="test-index", body=doc)
    except Exception as e:
        print(f"Could not write to Elasticsearch - {e}")
        response = flask.jsonify({"body": f"Error storing training details"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    response = flask.jsonify({"body": "Successfully written to db"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


if __name__ == "__main__":
    app.run()