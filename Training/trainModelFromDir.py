import sys, os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from keras.models import Sequential, load_model
from keras.layers import Conv2D, MaxPooling2D, Dense, Activation, Dropout, Flatten, BatchNormalization
from keras.initializers import  RandomNormal
from tensorflow.keras.callbacks import ReduceLROnPlateau, TensorBoard, EarlyStopping, ModelCheckpoint

batchSize = 50
imgHeight = 48
imgWidth = 48

def main():
    try:
        dataSetPath = sys.argv[1]
        outputModelDirectory = sys.argv[2]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)

    trainingData = tf.keras.preprocessing.image_dataset_from_directory(
        dataSetPath,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(imgHeight, imgWidth),
        batch_size=batchSize)

    validationData = tf.keras.preprocessing.image_dataset_from_directory(
        dataSetPath,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(imgHeight, imgWidth),
        batch_size=batchSize)

    print(trainingData.class_names)

    model = tf.keras.Sequential([
        layers.experimental.preprocessing.Rescaling(1./255),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(128, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(7)
    ])

    model.compile(
        optimizer='adam',
        loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])

    # Add callbacks
    cbLrReducer = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=3, verbose=1) # Reduce learning rate if there is no improvement on the value of the loss function
    # cbEarlyStopper = EarlyStopping(monitor='val_loss', min_delta=0, patience=8, verbose=1, mode='auto') # Stop training the model if it's overfitting
    cbCheckpoint = ModelCheckpoint(outputModelDirectory, monitor='val_accuracy', verbose=1, save_best_only=True) # Save model at the end of the epoch (if there's an improvement on the previous epoch's accuracy)

    model.fit(
        trainingData,
        validation_data=validationData,
        epochs=100,
        callbacks=[cbLrReducer, cbCheckpoint]
    )

    model.save(outputModelDirectory)


if __name__ == "__main__":
    main()