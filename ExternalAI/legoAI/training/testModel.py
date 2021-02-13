import sys, os
import tensorflow as tf
import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt

imgHeight = 200
imgWidth = 200
classNames = ['11214', '18651', '2357', '3003', '3004', '3005', '3022', '3023', '3024', '3040', '3069', '32123', '3673', '3713', '3794', '6632']

def main():
    try:
        modelDir = sys.argv[1]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)

    model = keras.models.load_model(modelDir)
    testImg = keras.preprocessing.image.load_img("dataSet\\exTest1.png")
    testArr = keras.preprocessing.image.img_to_array(testImg)
    testArr = np.array([testArr])
    probabilityModel = tf.keras.Sequential([model,tf.keras.layers.Softmax()]) # Create model to convert logits to probabilities
    predictions = probabilityModel.predict(testArr)
    # Predictions is list of lists, each list showing how confident the model is on each label
    # np.argmax returns index of highest value in list
    # so we just map that index to the index of the emotion codes to find what it thinks the emotion is
    print(predictions)
    print("======================PREDICTION======================")
    print(f"Predicted type: {classNames[np.argmax(predictions[0])]}")
    print("======================================================")

    # print(predictions)
    # print(np.argmax(predictions[0]))
    # print(emotionCodes[np.argmax(predictions[0])])
    plt.bar(classNames, predictions[0])
    plt.xticks(classNames)
    plt.show()

if __name__ == "__main__":
    main()