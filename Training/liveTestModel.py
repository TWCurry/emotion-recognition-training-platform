import sys, cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

emotionNames = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"]

# Load model
try:
    modelDir = sys.argv[1]
except Exception as e:
    print("Invalid parameters.")
    sys.exit(1)

model = load_model(modelDir)

# Haar-Cascade
faceCascade = cv2.CascadeClassifier('dataSet\haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
cv2.namedWindow("output", cv2.WINDOW_NORMAL)

while True:
    _, img = cap.read()

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect the faces
    faces = faceCascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        faceImage = gray[y:y+w,x:x+h]
        faceImage = cv2.resize(faceImage,(48,48))
        imgArr = image.img_to_array(faceImage)
        imgArr = np.expand_dims(imgArr, axis = 0)
        predictions = model.predict(imgArr)
        emotion = emotionNames[np.argmax(predictions[0])]
        cv2.putText(img, emotion, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow('output', img)
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break
        

cap.release()