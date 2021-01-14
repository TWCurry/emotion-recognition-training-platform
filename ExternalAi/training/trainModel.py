import sys
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint

batchSize = 20
imgHeight = 200
imgWidth = 200

def main():
    try:
        dataSetDir = sys.argv[1]
    except Exception as e:
        print("Invalid parameters.")
        sys.exit(1)

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
    print(f"Found class names {trainingDataset.class_names}")

    # Configure dataset for performance
    AUTOTUNE = tf.data.experimental.AUTOTUNE
    trainingDataset = trainingDataset.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    validationDataset = validationDataset.cache().prefetch(buffer_size=AUTOTUNE)

    # Create model (model shape and size to be investigated, maybe improved)
    model = keras.Sequential([
        layers.experimental.preprocessing.Rescaling(1./255, input_shape=(imgHeight, imgWidth, 3)),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(16)
    ])

    # Compile model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    print("Model summary:")
    print(model.summary())

    # Add callbacks
    cbLrReducer = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=3, verbose=1) # Reduce learning rate if there is no improvement on the value of the loss function
    cbEarlyStopper = EarlyStopping(monitor='val_loss', min_delta=0, patience=8, verbose=1, mode='auto') # Stop training the model if it's overfitting
    cbCheckpoint = ModelCheckpoint("outputModel4", monitor='val_accuracy', verbose=1, save_best_only=True) # Save model at the end of the epoch (if there's an improvement on the previous epoch's accuracy)

    # Train model
    epochs=30
    model.fit(
        trainingDataset,
        validation_data=validationDataset,
        batch_size=batchSize,
        epochs=epochs,
        callbacks=[cbLrReducer, cbEarlyStopper, cbCheckpoint]
    )
    model.save("outputModel4")
    

if __name__ == "__main__":
    main()