import shutil
import flask, json, sys, os
from flask import Flask, request
from shutil import copyfile
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint

# Initialisation
app = Flask(__name__)
# Level of training data over which we then train model
trainingThreshold = 20
batchSize = 10
# If emotion is positive, we assume the AI was correct
positiveEmotions = ["Happy"]

# If emotion is negative, we assume the AI was incorrect
negativeEmotions = ["Angry", "Disgusted", "Sad"]

# If emotion is neutral, we cannot make an assumption on whether the AI was correct or not
neutralEmotions = ["Afraid", "Neutral", "Surprised"]

@app.route("/storeDetails", methods=["POST"])
def storeDetails():
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

    if not(emotion in negativeEmotions):
        print(f"No inference needed as emotion was {emotion}")
        response = flask.jsonify({"body": f"No inference needed as emotion was {emotion}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
    else:
        print(f"Emotion was {emotion} - storing for training later")

    data = {
        "modelName": modelName,
        "imageNames": imageNames,
        "typeToIdentify": typeToIdentify,
        "responseIndex": responseIndex,
        "emotion": emotion
    }

    try:
        f = open("config.json", "r")
        configData = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f"Could not load config - {e}")
        response = flask.jsonify({"body": f"Could not load config - {e}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    f = open("trainingDetails.txt", "a+")
    f.write(f"{json.dumps(data)}\n")
    f.close()

    existingTrainingDetails = readTrainingDetails()
    
    for existingDataModelName, trainingData in existingTrainingDetails.items():
        if existingDataModelName == modelName and len(trainingData) > trainingThreshold:
            print(f"Model {modelName} has reached the threshold for training data, training model...")
            modelConfigData = []
            for config in configData["customerModels"]:
                if config["modelName"] == modelName:
                    modelConfigData = config
            if modelConfigData == []:
                print(f"Could not find config for {modelName}")
                response = flask.jsonify({"body": f"Could not find config for {modelName}"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 500
            generateDataset(trainingData, modelConfigData)
            trainModel(modelConfigData, modelName)
            clearTrainingDetails()
            shutil.rmtree(f"dataSets/{modelConfigData['datasetName']}")

    response = flask.jsonify({"body": f"Details stored successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

def readTrainingDetails():
    existingTrainingDetails = {}
    f = open("trainingDetails.txt", "r")
    for line in f:
        line = json.loads(line)
        if line["modelName"] in existingTrainingDetails:
            existingTrainingDetails[line["modelName"]].append(line)
        else:
            existingTrainingDetails[line["modelName"]] = []
            existingTrainingDetails[line["modelName"]].append(line)
    f.close()
    return existingTrainingDetails

def clearTrainingDetails():
    f = open("trainingDetails.txt", "w")
    f.write("")
    f.close()

def generateDataset(trainingData, configData):
    print(configData)
    for data in trainingData:
        for image in data["imageNames"]:
            try:
                copyfile(f"{configData['datasetPath']}{image}", f"dataSets/{image}")
            except IOError as io_err:
                os.makedirs(os.path.dirname(f"dataSets/{image}"))
                copyfile(f"{configData['datasetPath']}{image}", f"dataSets/{image}")
    

def trainModel(configData, modelName):
    # Identify model config data
    modelConfig = configData

    dataSetDir = f"dataSets/{configData['datasetName']}"

    # Load image dimensions
    imgHeight = int(modelConfig["imageDimensions"][0])
    imgWidth = int(modelConfig["imageDimensions"][1])
    
    # Load dataset
    trainingDataset = tf.keras.preprocessing.image_dataset_from_directory(
        dataSetDir,
        validation_split=0.2, # 20% of images will be used for validation
        subset="training",
        seed=123,
        image_size=(imgHeight, imgWidth),
        batch_size=batchSize
    )
    validationDataset = tf.keras.preprocessing.image_dataset_from_directory(
        dataSetDir,
        validation_split=0.2, # 20% of images will be used for validation
        subset="validation",
        seed=123,
        image_size=(imgHeight, imgWidth),
        batch_size=batchSize
    )
    print(trainingDataset)
    print(f"Found class names {trainingDataset.class_names}")
    

    # Load model
    print("Loading model...")
    model = keras.models.load_model(f"{modelConfig['modelPath']}")

    # Add callbacks
    cbLrReducer = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=3, verbose=1) # Reduce learning rate if there is no improvement on the value of the loss function
    cbEarlyStopper = EarlyStopping(monitor='val_loss', min_delta=0, patience=7, verbose=1, mode='auto') # Stop training the model if it's overfitting
    cbCheckpoint = ModelCheckpoint(modelConfig['modelPath'], monitor='val_accuracy', verbose=1, save_best_only=True) # Save model at the end of the epoch (if there's an improvement on the previous epoch's accuracy)

    # Train model
    print("Training model...")
    epochs=30
    model.fit(
        trainingDataset,
        validation_data=validationDataset,
        batch_size=batchSize,
        epochs=epochs,
        callbacks=[cbLrReducer, cbEarlyStopper, cbCheckpoint]
    )

    # Save model
    print("Saving model...")
    model.save(modelConfig['modelPath'])

if __name__ == "__main__":
    app.run(port=5001)