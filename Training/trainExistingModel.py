import sys, os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ReduceLROnPlateau, TensorBoard, EarlyStopping, ModelCheckpoint

batchSize = 50
imgHeight = 48
imgWidth = 48
emotionCodes = ["AN", "DI", "FE", "HA", "SA", "SU", "NE"]


def main():
    try:
        dataSetPath = sys.argv[1]
        outputModelDirectory = sys.argv[2]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)

    try:
        with open(dataSetPath) as f:
            csvData = f.read().splitlines()
    except Exception as e:
        print(f"Could not read {dataSetPath} - {e}")
        sys.exit(1)

    print(f"Creating dataset from {dataSetPath} ...")
    trainingData = []
    trainingLabels = []
    validationData = []
    validationLabels = []
    firstRecord = True
    for row in csvData: #For each record in csv (apart from first headers row)
        row = row.split(",")
        if firstRecord:
            firstRecord = False
        else:
            record = {"emotion": int(row[0]), "pixels": row[1], "usage": row[2]}
            pixels = record['pixels'].split(" ") # Split pixels into array, separated by space
            for i in range(len(pixels)): #Force conversion to integer
                pixels[i] = int(pixels[i])
            if record['usage'] == 'Training':
                trainingData.append(np.array(pixels))
                trainingLabels.append(int(record['emotion']))
            elif record['usage'] == 'PublicTest':
                validationLabels.append(int(record['emotion']))
                validationData.append(np.array(pixels))
    
    # Convert to numpy array
    trainingData = np.array(trainingData)
    trainingLabels = np.array(trainingLabels)
    validationData = np.array(validationData)
    validationLabels = np.array(validationLabels)

    trainingData = trainingData.reshape(trainingData.shape[0], 48, 48, 1)
    validationData = validationData.reshape(validationData.shape[0], 48, 48, 1)

    trainingLabels= keras.utils.to_categorical(trainingLabels, num_classes=7)
    validationLabels = keras.utils.to_categorical(validationLabels, num_classes=7)

    # Create augmented data
    augmentedData = keras.Sequential([
        layers.experimental.preprocessing.RandomFlip("horizontal", input_shape=(imgHeight, imgWidth, 1)),
        layers.experimental.preprocessing.RandomRotation(0.2),
        layers.experimental.preprocessing.RandomZoom(0.2),
    ])

    model = keras.models.load_model(outputModelDirectory)
    model.evaluate(trainingData, trainingLabels)

    # Compile model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    print("Model summary:")
    print(model.summary())

    # Add callbacks
    cbLrReducer = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=3, verbose=1) # Reduce learning rate if there is no improvement on the value of the loss function
    cbEarlyStopper = EarlyStopping(monitor='val_loss', min_delta=0, patience=8, verbose=1, mode='auto') # Stop training the model if it's overfitting
    cbCheckpoint = ModelCheckpoint(outputModelDirectory, monitor='val_accuracy', verbose=1, save_best_only=True) # Save model at the end of the epoch (if there's an improvement on the previous epoch's accuracy)

    # Train model
    epochs=30
    model.fit(
        trainingData,
        trainingLabels,
        validation_data=(validationData, validationLabels),
        batch_size=batchSize,
        epochs=epochs,
        callbacks=[cbLrReducer, cbEarlyStopper, cbCheckpoint]
    )
    scores = model.evaluate(np.array(validationData), np.array(validationLabels), batch_size=batchSize)
    print(f"Loss: {scores[0]}")
    print(f"Accuracy: {int(scores[1])*100}%")
    model.save(outputModelDirectory)
    

if __name__ == "__main__":
    main()