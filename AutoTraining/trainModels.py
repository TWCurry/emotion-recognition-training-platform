import json, sys, os
from google.cloud import firestore, storage

modelFilenames = [] # Stores list of filenames, to delete after execution

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
            generateTrainingData(configData, modelName, responseIndex, typeToIdentify, imageNames)
        elif emotion in neutralEmotions:
            print("Emotion is neutral - no inference possible.")
        else:
            print(f"Invalid emotion {emotion}.")
            sys.exit(1)

        # Delete doc
        # rawDoc.delete()

    # Delete models
    # for fileName in modelFilenames:
    #     os.remove(fileName)

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

    # Fetch training image
    fileType = imageNames[responseIndex].split(".")[-1]
    bucketName = modelConfig["datasetBucket"]
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob(imageNames[responseIndex])
    blob.download_to_filename(f"image.{fileType}")
    os.remove(f"image.{fileType}")


if __name__ == "__main__":
    main()