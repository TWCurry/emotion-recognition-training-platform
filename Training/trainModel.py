import sys, os
import tensorflow as tf
from tensorflow.python.ops.gen_batch_ops import batch

batchSize = 32
imgHeight = 762
imgWidth = 562

def main():
    try:
        dataSetDir = sys.argv[1]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)
    
    if not (os.path.exists(dataSetDir)):
        print(f"Directory {dataSetDir} does not exist.")
        sys.exit(1)

    dataset = createDataset(dataSetDir)

def createDataset(dataSetDir):
    print(f"Creating dataset from {dataSetDir} directory...")
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


if __name__ == "__main__":
    main()