# emotion-recognition-training-platform
Uni final year project. Platform that uses deep-learning facial emotion recognition to generate training data for AI

# Setup Instructions
Note: This is purely for the offline implementation. The GCP implementation takes a lot more setup, and will be documented later.

1. Clone the repo, checkout the main branch.
2. Install dependencies. The system requires Python 3.7 or higher, as well as the following Python libraries (can be installed using Pip):
    * opencv-python
    * tensorflow
    * flask
    * numpy
    * tflite_runtime (see https://www.tensorflow.org/lite/guide/python for instructions)
2. Download the trained FER model. It can be fetched from https://fer-application-cloudformation-templates.s3.eu-west-2.amazonaws.com/model.tflite.
3. Copy the downloaded FER model (model.tflite) to /API/Offline/model.tflite
4. Download the dataset (for the external AI model). It can be downloaded from https://fer-application-cloudformation-templates.s3.eu-west-2.amazonaws.com/legoDataset.zip.
5. Extract the dataset to /offlineBackend/API/ (it should create a "loegoDataset" folder.)
6. Run services. To run each service, you must open an individual terminal window (either in Linux, and navigate to the following directories to run each microservice:
    * FER microservice: /API/Offline
    * Autotraining microservice: /AutoTraining/Offline
    * Metrics microservice: /Metrics/Backend

In all of these directories, run the command py `api.py` (on Windows) or `python api.py` (on Mac OS/BSD/*nix).

7. Run the external AI service. This can be done (in another separate terminal window from those running the other services) by navigating to /ExternalAI/legoAI/offlineBackend/API and running `py api.py` (Windows) or `python api.py` (on Mac OS/BSD/*nix).

8. Open Frontends. To open the frontend for the external AI service, navigate to /ExternalAI/legoAI/frontend, and open the index.html file (which will also load the associated CSS, JS etc when it opens in your browser). To open the metrics dashboard, navigate to /Metrics/Frontend, and open index.html. Note that no data will load in the metrics dashboard if either the metrics microservice is not running, or there has been no training yet performed (and stored in the metrics database).