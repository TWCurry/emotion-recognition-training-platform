import json, sys, os, zipfile, shutil, cv2
import tensorflow as tf
import numpy as np
from google.cloud import firestore, storage
from tensorflow import keras
from tensorflow.keras import layers

modelFilenames = [] # Stores list of filenames, to delete after execution
modelDirectories = [] # Stores list of directories, to delete after execution

# If emotion is positive, we assume the AI was correct
positiveEmotions = ["Happy"]

# If emotion is negative, we assume the AI was incorrect
negativeEmotions = ["Angry", "Disgusted", "Sad"]

# If emotion is neutral, we cannot make an assumption on whether the AI was correct or not
neutralEmotions = ["Afraid", "Neutral", "Surprised"]

# Instantiate Google Cloud Storage client
storage_client = storage.Client()

def main():
    # Load Config
    try:
        f = open("config.json", "r")
        configData = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f"Could not load config - {e}")
        sys.exit(1)

    # Instantiate Google Firestore connection
    db = firestore.Client()
    

    # Download models
    for customerModel in configData["customerModels"]:
        print(f"Downloading model for {customerModel['modelName']}...")
        bucket = storage_client.bucket(customerModel["modelBucket"])
        blob = bucket.blob(customerModel["modelPath"])
        if not(os.path.exists(f"{customerModel['modelName']}.zip")): # If statement to speed up testing
            blob.download_to_filename(f"{customerModel['modelName']}.zip")
        modelFilenames.append(f"{customerModel['modelName']}.zip")
        modelDirectories.append(customerModel["modelName"])

    # Fetch fer data
    collection = db.collection("inferenceData")
    docs = collection.stream()
    for rawDoc in docs:
        doc = rawDoc.to_dict()
        # Fetch fields
        try:
            modelName = doc["modelName"]
            emotion = doc["emotion"]
            responseIndex = int(doc["responseIndex"])
            typeToIdentify = doc["typeToIdentify"]
            imageNames = doc["imageNames"].split(",")
        except Exception as e:
            print(f"Missing fields in Firebase entry - {e}")
            sys.exit(1)

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

        # Delete doc
        # rawDoc.delete()

    # Delete models
    for fileName in modelFilenames:
        os.remove(fileName)
    for dir in modelDirectories:
        print(f"Removing {dir} directory...")
        shutil.rmtree(dir)

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
    fileType = imageNames[responseIndex].split(".")[-1]
    bucketName = modelConfig["datasetBucket"]
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob(imageNames[responseIndex])
    blob.download_to_filename(f"image.{fileType}")

    # Load image
    im = cv2.imread(f"image.{fileType}")
    trainingData = []
    trainingLabels = []
    trainingData.append(np.array(im))
    trainingLabels.append(str(classNames.index(typeToIdentify)))
    trainingData = np.array(trainingData)
    trainingLabels = np.array(trainingLabels)
    print(typeToIdentify)
    print(classNames)
    print(trainingLabels)
    trainingLabels = keras.utils.to_categorical(trainingLabels, num_classes=int(modelConfig["numClasses"]))
    print(trainingLabels)
    trainingData = trainingData.reshape(trainingData.shape[0], height, width, 3)

    # Unzip model
    with zipfile.ZipFile(f"{modelConfig['modelName']}.zip","r") as zip_ref:
        zip_ref.extractall(modelConfig['modelName'])

    # Load model
    model = keras.models.load_model(f"{modelConfig['modelName']}")
    print(model.summary())

    # Compile model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    # Train model
    epochs=5
    model.fit(
        trainingData,
        trainingLabels,
        batch_size=1,
        epochs=epochs
    )
    model.save("outputModel4")

    os.remove(f"image.{fileType}")


if __name__ == "__main__":
    main()