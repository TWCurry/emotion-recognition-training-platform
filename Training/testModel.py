import sys, os
import tensorflow as tf
import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt

imgHeight = 762
imgWidth = 562
emotionCodes = ["AF", "AN", "DI", "HA", "NE", "SA", "SU"]
emotionNames = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"]

def main():
    try:
        modelDir = sys.argv[1]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)

    model = keras.models.load_model(modelDir)
    testImg = keras.preprocessing.image.load_img("dataSet/test2.jpg")
    testArr = keras.preprocessing.image.img_to_array(testImg)
    testArr = np.array([testArr])
    probabilityModel = tf.keras.Sequential([model,tf.keras.layers.Softmax()]) # Create model to convert logits to probabilities
    predictions = probabilityModel.predict(testArr)
    # Predictions is list of lists, each list showing how confident the model is on each label
    # np.argmax returns index of highest value in list
    # so we just map that index to the index of the emotion codes to find what it thinks the emotion is
    print(predictions)
    print("======================PREDICTION======================")
    print(f"Predicted emotion: {emotionNames[np.argmax(predictions[0])]}")
    print("======================================================")

    # print(predictions)
    # print(np.argmax(predictions[0]))
    # print(emotionCodes[np.argmax(predictions[0])])
    plt.bar(emotionCodes, predictions[0])
    plt.xticks(emotionCodes)
    plt.show()

if __name__ == "__main__":
    main()