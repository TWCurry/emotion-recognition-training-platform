import json, sys, os, zipfile, shutil, cv2, flask
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from flask import Flask, request

# Initialisation
app = Flask(__name__)

modelFilenames = [] # Stores list of filenames, to delete after execution
modelDirectories = [] # Stores list of directories, to delete after execution

# If emotion is positive, we assume the AI was correct
positiveEmotions = ["Happy"]

# If emotion is negative, we assume the AI was incorrect
negativeEmotions = ["Angry", "Disgusted", "Sad"]

# If emotion is neutral, we cannot make an assumption on whether the AI was correct or not
neutralEmotions = ["Afraid", "Neutral", "Surprised"]

@app.route("/trainModel", methods=["POST"])
def trainModel():
    try:
        f = open("config.json", "r")
        configData = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f"Could not load config - {e}")
        sys.exit(1)
    try:
        modelName = str(request.form.getlist('modelName')[0])
        imageNames = json.loads(request.form.getlist('imageNames')[0])
        typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
        responseIndex = str(request.form.getlist('responseIndex')[0])
        emotion = str(request.form.getlist('emotion')[0])
    except Exception as e:
        print(f"Failed to get parameters - {e}")
        response = flask.jsonify({"body": f"Invalid parameters - {e}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    if emotion in positiveEmotions:
        print("Emotion is positive - no inference needed.")
    elif emotion in negativeEmotions:
        print("Emotion is negative - beginning inference...")
        generateTrainingData(configData, modelName, responseIndex, typeToIdentify, imageNames)
    elif emotion in neutralEmotions:
        print("Emotion is neutral - no inference possible.")
    else:
        print(f"Invalid emotion {emotion}.")
        sys.exit(1)

    response = flask.jsonify({"body": f"Training succeeded"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

def generateTrainingData(configData, modelName, responseIndex, typeToIdentify, imageNames):
    # Identify model config data
    modelConfig = {}
    modelIdentified = False
    for customerModel in configData["customerModels"]:
        if customerModel["modelName"] == modelName:
            modelIdentified = True
            modelConfig = customerModel
    if modelIdentified == False:
        print(f"Could not fetch configuration for {modelName} model.")
        sys.exit(1)
    classNames = modelConfig["classNames"]
    
    # Load image dimensions
    height = int(modelConfig["imageDimensions"][0])
    width = int(modelConfig["imageDimensions"][1])

    # Fetch training image
    print("Downloading new training image...")
    responseIndex = int(responseIndex)
    imagePath = f"{modelConfig['datasetPath']}{imageNames[responseIndex]}"
    f = open(imagePath, "rb")
    f.read()
    f.close()

    # Load image
    print("Loading new training image...")
    im = cv2.imread(imagePath)
    trainingData = []
    trainingLabels = []
    trainingData.append(np.array(im))
    trainingLabels.append(str(classNames.index(typeToIdentify)))
    trainingData = np.array(trainingData)
    trainingLabels = np.array(trainingLabels)
    trainingLabels = keras.utils.to_categorical(trainingLabels, num_classes=int(modelConfig["numClasses"]))
    trainingData = trainingData.reshape(trainingData.shape[0], height, width, int(modelConfig["colourChannels"]))

    # Load model
    print("Loading model...")
    model = keras.models.load_model(f"{modelConfig['modelPath']}")
    print(model.summary())

    # Compile model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    # Train model
    print("Training model...")
    epochs=5
    model.fit(
        trainingData,
        trainingLabels,
        batch_size=1,
        epochs=epochs
    )

    # Save model
    print("Saving model...")
    model.save(modelConfig['modelPath'])


if __name__ == "__main__":
    app.run(port=5001)