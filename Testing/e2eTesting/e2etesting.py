from typing import DefaultDict
import requests, json, sys, random, os

trainingCycles = 1000
ferApiUrl = "http://localhost:5000"
legoApiUrl = "http://localhost:5003"

positiveEmotions = ["Happy"]

negativeEmotions = ["Angry", "Disgusted", "Sad"]

neutralEmotions = ["Afraid", "Neutral", "Surprised"]

def main():
    try:
        modelName = sys.argv[1]
        dataSetPath = sys.argv[2]
        dataSetName = sys.argv[3]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)
    
    classNames = next(os.walk(dataSetPath))[1]

    for cycle in range(trainingCycles):
        print(f"Cycle {cycle} out of {trainingCycles}")
        # Randomly select 2 image classes
        selectedClassNames = []
        selectedClassNames.append(classNames[random.randint(0, len(classNames)-1)])
        selectedClassNames.append(classNames[random.randint(0, len(classNames)-1)])
        # Make sure the 2 classes are separate
        while selectedClassNames[1] == selectedClassNames[0]:
            selectedClassNames[1] = classNames[random.randint(0, len(classNames)-1)]
        # Randomly select one image from each class
        imageNames = []
        imageNames.append(random.choice(os.listdir(f"{dataSetPath}/{selectedClassNames[0]}")))
        imageNames.append(random.choice(os.listdir(f"{dataSetPath}/{selectedClassNames[1]}")))
        # Get AI to identify the image containing the chosen type (always at index 0)
        data = {
            "imageNames": f"[\"{dataSetName}/{selectedClassNames[0]}/{imageNames[0]}\",\"{dataSetName}/{selectedClassNames[1]}/{imageNames[1]}\"]",
            "typeToIdentify": selectedClassNames[0]
        }
        r = requests.post(legoApiUrl+"/identifyBrickType", data=data)

        # If the AI has chosen index 0, it is correct, if not it is wrong
        
        if r.json()["body"][0] == 0:
            aiIncorrect = False
        elif r.json()["body"][0] == 1:
            aiIncorrect = True
        else:
            print("Error: Invalid image indice")

        if aiIncorrect:
            # If the AI was incorrect, send back a negative emotion to train the model
            print("AI was incorrect")
            params = {
                "emotion": negativeEmotions[random.randint(0, len(negativeEmotions)-1)],
                "imageNames": f"[\"{dataSetName}/{selectedClassNames[0]}/{imageNames[0]}\",\"{dataSetName}/{selectedClassNames[1]}/{imageNames[1]}\"]",
                "modelName": modelName,
                "responseIndex": "1",
                "typeToIdentify": selectedClassNames[0]
            }
        else:
            # If the AI was correct, send back a positive emotion
            print("AI was correct")
            params = {
                "emotion": positiveEmotions[random.randint(0, len(positiveEmotions)-1)],
                "imageNames": f"[\"{dataSetName}/{selectedClassNames[0]}/{imageNames[0]}\",\"{dataSetName}/{selectedClassNames[1]}/{imageNames[1]}\"]",
                "modelName": modelName,
                "responseIndex": "0",
                "typeToIdentify": selectedClassNames[0]
            }
        # Call the autotraining API to train the model if needed
        r = requests.post(ferApiUrl+"/uploadTrainingDetails", data=params)
        print(r.json())
    

    

if __name__ == "__main__":
    main()