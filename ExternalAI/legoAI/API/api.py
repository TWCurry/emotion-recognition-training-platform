import flask, random, base64, cv2, sys, google, json, os
from flask import Flask, request
from google.cloud import storage
import numpy as np
import tensorflow as tf
from tensorflow import keras
# Initialisation
classNames = ['11214', '18651', '2357', '3003', '3004', '3005', '3022', '3023', '3024', '3040', '3069', '32123', '3673', '3713', '3794', '6632']
app = Flask(__name__)
try:
    client = storage.Client()
except google.auth.exceptions.DefaultCredentialsError as e:
    print(e)
    sys.exit()
bucketName = "tc-fer-application-datasets"
folderPrefix="legoDataset"
bucket = client.bucket(bucketName)

@app.route("/fetchImages", methods=["GET"])
def fetchImages():
    imgNames = []
    returnData = {}
    try:
        for blob in client.list_blobs(bucketName, prefix="legoDataset"):
            imgNames.append(blob)
        for i in range(2):
            index = random.randint(0, len(imgNames)-1)
            blob = bucket.blob(imgNames[index].name)
            data = blob.download_as_bytes()
            b64Data = base64.b64encode(data)
            returnData[i] = {imgNames[index].name:(str(b64Data))}
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
    # Load model
    print("Loading model...")
    model = keras.models.load_model("model")
    probabilityModel = tf.keras.Sequential([model,tf.keras.layers.Softmax()]) # Create model to convert logits to probabilities

    imageNames = json.loads(request.form.getlist('imageNames')[0])
    typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
    indicesContainingImage = []
    fileNames = []

    for i in range(len(imageNames)):
        npArr = np.zeros((200,200))
        print(imageNames[i])
        blob = bucket.blob(imageNames[i])
        fileName = imageNames[i].split("/")[-1]
        fileNames.append(fileName)
        blob.download_to_filename(fileName)

        img = keras.preprocessing.image.load_img(fileName)
        imgArr = keras.preprocessing.image.img_to_array(img)
        imgArr = np.array([imgArr])

        predictions = probabilityModel.predict(imgArr)
        classType = classNames[np.argmax(predictions[0])]
        # print(predictions)
        print(classType)

        # If current image contains chosen brick type:
        if classType == typeToIdentify:
            indicesContainingImage.append(i)

    for file in fileNames:
        try:
            os.remove(file)
        except:
            print(f"Warning - could not delete file {file}.")

    response = flask.jsonify({"body": indicesContainingImage})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

if __name__ == "__main__":
    app.run()