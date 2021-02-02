import boto3, base64, cv2, json, flask ,os
import numpy as np
# from PIL import Image
from flask import Flask, request
from urllib.parse import unquote
import tflite_runtime.interpreter as tflite

emotionNames = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"]

# Initialisation
app = Flask(__name__)

@app.route("/uploadImage", methods=["POST"])
def infer():
    # Load Config
    try:
        f = open("config.json", "r")
        configData = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f"Could not load config - {e}")
        return createResponse(500, f"Could not load config - {e}")

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

    imgB64 = ""

    for (x, y, w, h) in faces:
        # Capture image of face, resize to 48x48
        faceImage = img[y:y+w,x:x+h]
        faceImage = cv2.resize(faceImage,(48,48))
        # Convert image to base64 for returning to client
        retval, buffer = cv2.imencode('.jpg', faceImage)
        imgB64 = base64.b64encode(buffer)
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

if __name__ == "__main__":
    app.run()