import flask, random, base64, cv2, sys, json, os, random
from flask import Flask, request
import numpy as np
import tensorflow as tf
from tensorflow import keras
# Initialisation
classNames = ['11214', '18651', '2357', '3003', '3004', '3005', '3022', '3023', '3024', '3040', '3069', '32123', '3673', '3713', '3794', '6632']
app = Flask(__name__)

@app.route("/fetchImages", methods=["GET"])
def fetchImages():
    imgNames = []
    returnData = {}
    try:
        for i in range(2):
            folder = random.choice(os.listdir("legoDataset"))
            imgName = random.choice(os.listdir(f"legoDataset/{folder}"))
            f = open(f"legoDataset/{folder}/{imgName}", "rb")
            data = f.read()
            f.close()
            b64Data = base64.b64encode(data)
            returnData[i] = {f"legoDataset/{folder}/{imgName}":(str(b64Data))}
    except Exception as e:
        print(f"Could not fetch Lego images - {e}")
        response = flask.jsonify({"body": "Could not fetch images"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    response = flask.jsonify({"body": returnData})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@app.route("/identifyBrickType", methods=["POST"])
def identifyBrickType():
    # Handle parameters
    try:
        imageNames = json.loads(request.form.getlist('imageNames')[0])
        typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
    except Exception as e:
        print(f"Invalid parameters - {e}")
        response = flask.jsonify({"body": "Invalid parameters"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    # Load model
    print("Loading model...")
    model = keras.models.load_model("model")
    probabilityModel = tf.keras.Sequential([model,tf.keras.layers.Softmax()]) # Create model to convert logits to probabilities

    indicesContainingImage = []
    fileNames = []

    for i in range(len(imageNames)):
        npArr = np.zeros((200,200))
        print(imageNames[i])

        img = keras.preprocessing.image.load_img(imageNames[i])
        imgArr = keras.preprocessing.image.img_to_array(img)
        imgArr = np.array([imgArr])

        predictions = probabilityModel.predict(imgArr)
        classType = classNames[np.argmax(predictions[0])]
        # print(predictions)
        print(classType)

        # If current image contains chosen brick type:
        if classType == typeToIdentify:
            indicesContainingImage.append(i)

    if len(indicesContainingImage) == 0:
        indicesContainingImage.append(random.choice([int(0), int(1)]))

    response = flask.jsonify({"body": indicesContainingImage})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

if __name__ == "__main__":
    app.run(port=5003)