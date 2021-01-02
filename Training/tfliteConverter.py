# Python file to convert Tensorflow model to Tensorflow lite model
import sys
import tensorflow as tf
from tensorflow import keras

def main():
    try:
        inputPath = sys.argv[1]
        outputPath = sys.argv[2]
    except Exception as e:
        print("Usage: python tfliteConverter.py inputModelPath outputPath")
        sys.exit(1)

    # Load model
    model = keras.models.load_model(inputPath)
    # Create converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tfliteModel = converter.convert()
    with open(outputPath, "wb") as f:
        f.write(tfliteModel)
    print(f"Conversion complete, written output model to {outputPath}.")

if __name__ == "__main__":
    main()