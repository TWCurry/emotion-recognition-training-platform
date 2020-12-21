import sys, os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.ops.gen_batch_ops import batch

batchSize = 10
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
    print(f"Found class names {trainingDataset.class_names}")

    # Configure dataset for performance
    AUTOTUNE = tf.data.experimental.AUTOTUNE
    trainingDataset = trainingDataset.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    validationDataset = validationDataset.cache().prefetch(buffer_size=AUTOTUNE)

    # Standardize data (rescale rgb values from 0-255 to 0-1)
    normalizationLayer = layers.experimental.preprocessing.Rescaling(1./255)

    # Create model (model shape and size to be investigated, maybe improved)

    classNo = 7
    model = keras.Sequential([
        layers.experimental.preprocessing.Rescaling(1./255, input_shape=(imgHeight, imgWidth, 3)),
        layers.experimental.preprocessing.RandomFlip("horizontal", input_shape=(imgHeight, imgWidth,3)), # Data augmentation
        layers.experimental.preprocessing.RandomRotation(0.1),# Data augmentation
        layers.experimental.preprocessing.RandomZoom(0.1), # Data augmentation
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2), # Dropout (for regularisation)
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(classNo)    ])

    # Compile model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    print("Model summary:")
    print(model.summary())

    # Train model
    epochs=10
    model.fit(
        trainingDataset,
        validation_data=validationDataset,
        epochs=epochs
    )
    model.save("outputModel")

if __name__ == "__main__":
    main()