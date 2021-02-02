import base64, cv2, json, flask, time
import numpy as np
# from PIL import Image
from flask import Flask, request
from urllib.parse import unquote
from google.cloud import firestore
import tflite_runtime.interpreter as tflite

emotionNames = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"]

# Initialisation
app = Flask(__name__)

@app.route("/uploadImage", methods=["POST"])
def infer():
    imageData = str(request.form.getlist('imageData')[0])
    print("Loading image...")
    imageData = unquote(imageData) # Url decode body
    imageData = imageData.split(",")[1] # Remove b64 header
    imageData = base64.b64decode(imageData) # decode base64 to bytes
    nparr = np.frombuffer(imageData, np.uint8) # Load image into numpy array
    img = cv2.imdecode(nparr, 0) # Convert to grayscale cv2 image
    imgArr = np.zeros((48,48)) # Empty array, will store the image data

    # Load Haar-Cascade
    print("Loading Haar-Cascade...")
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Detect the faces in the image
    print("Detecting faces in image...")
    faces = faceCascade.detectMultiScale(img, 1.1, 4)
    if(len(faces)) == 0:
        print("No faces found.")
        return createResponse(200, "No faces found.")

    for (x, y, w, h) in faces:
        # Capture image of face, resize to 48x48
        faceImage = img[y:y+w,x:x+h]
        faceImage = cv2.resize(faceImage,(48,48))
        # Convert to numpy array and expand dimensions to be used as inputs for models
        imgArr = np.array(faceImage, dtype=np.float32)
        imgArr = np.expand_dims(imgArr, axis=0)

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

    response = flask.jsonify({
        "statusCode": 200,
        "body": "Function executed successfully",
        "emotion": emotion
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def createResponse(statusCode, body):
    # Simple function to generate HTTP response with correct headers (to reduce repeated code)
    response = flask.jsonify({
        "statusCode": statusCode,
        "body": str(body)
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/uploadTrainingDetails", methods=["POST"])
def storeTrainingData():
    # Parameters
    try:
        modelName = str(request.form.getlist('modelName')[0])
        imageNames = json.loads(request.form.getlist('imageNames')[0])
        typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
        responseIndex = str(request.form.getlist('responseIndex')[0])
        emotion = str(request.form.getlist('emotion')[0])
    except Exception as e:
        print(f"Failed to get parameters - {e}")
        response = flask.jsonify({
            "statusCode": 400,
            "body": "Invalid parameters."
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # Instantiate Firebase connection
    db = firestore.Client()

    # Write training data to DB
    timestamp = int(time.time())
    document = db.collection("inferenceData").document(f"{timestamp}")
    document.set({
        "modelName": modelName,
        "imageNames": (str(imageNames)),
        "typeToIdentify": typeToIdentify,
        "responseIndex": responseIndex,
        "emotion": emotion
    })


if __name__ == "__main__":
    app.run()