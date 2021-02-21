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
    print("Downloading models...")
    for customerModel in configData["customerModels"]:
        print(f"Downloading model for {customerModel['modelName']}...")
        bucket = storage_client.bucket(customerModel["modelBucket"])
        blob = bucket.blob(customerModel["modelPath"])
        if not(os.path.exists(f"{customerModel['modelName']}.zip")): # If statement to speed up testing
            blob.download_to_filename(f"{customerModel['modelName']}.zip")
        modelFilenames.append(f"{customerModel['modelName']}.zip")
        modelDirectories.append(customerModel["modelName"])
    print("Downloaded all configured models.")

    # Fetch fer data
    collection = db.collection("inferenceData")
    docs = collection.stream()
    for rawDoc in docs:
        print("=====================================================")
        print(f"Reading document ID: {rawDoc.id}")
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

        # Delete docs
        deleteCollection()

    # Delete models
    print("Deleting model zip files...")
    for fileName in modelFilenames:
        os.remove(fileName)
    print("Deleting extracted models")
    for dir in modelDirectories:
        print(f"Removing {dir} directory...")
        shutil.rmtree(dir)

def deleteCollection(collection, batchSize):
    docs = collection.limit(batchSize).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batchSize:
        return deleteCollection(collection, batchSize)

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
    fileType = imageNames[responseIndex].split(".")[-1]
    bucketName = modelConfig["datasetBucket"]
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob(imageNames[responseIndex])
    blob.download_to_filename(f"image.{fileType}")

    # Load image
    print("Loading new training image...")
    im = cv2.imread(f"image.{fileType}")
    trainingData = []
    trainingLabels = []
    trainingData.append(np.array(im))
    trainingLabels.append(str(classNames.index(typeToIdentify)))
    trainingData = np.array(trainingData)
    trainingLabels = np.array(trainingLabels)
    trainingLabels = keras.utils.to_categorical(trainingLabels, num_classes=int(modelConfig["numClasses"]))
    trainingData = trainingData.reshape(trainingData.shape[0], height, width, int(modelConfig["colourChannels"]))

    # Unzip model
    print("Unzipping model...")
    with zipfile.ZipFile(f"{modelConfig['modelName']}.zip","r") as zipRef:
        zipRef.extractall(modelConfig['modelName'])

    # Load model
    print("Loading model...")
    model = keras.models.load_model(f"{modelConfig['modelName']}")
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
    model.save(f"{modelConfig['modelName']}-out")
    shutil.make_archive(f"{modelConfig['modelName']}-out", 'zip', f"{modelConfig['modelName']}-out") # Zip directory

    # Uploading model to GCP
    uploadFile(f"{modelConfig['modelName']}-out.zip", modelConfig["modelBucket"], modelConfig["modelPath"])

    # Remove training image
    os.remove(f"image.{fileType}")

def uploadFile(fileToUpload, bucketName, path):
    # Function to upload fileToUpload to the bucket and path specified
    print(f"Uploading {fileToUpload} to {bucketName} bucket at {path}...")
    client = storage.Client()
    bucket = client.bucket(bucketName)
    blob = bucket.blob(path)
    blob.upload_from_filename(fileToUpload)

if __name__ == "__main__":
    main()