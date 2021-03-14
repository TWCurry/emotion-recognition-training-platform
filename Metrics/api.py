import json, flask
from flask import Flask, request

# Initialisation
app = Flask(__name__)

@app.route("/logMetric", methods=["POST"])
def logMetric():
    try:
        modelName = str(request.form.getlist('modelName')[0])
        imageNames = json.loads(request.form.getlist('imageNames')[0])
        typeToIdentify = str(request.form.getlist('typeToIdentify')[0])
        responseIndex = str(request.form.getlist('responseIndex')[0])
        emotion = str(request.form.getlist('emotion')[0])
    except Exception as e:
        print(f"Failed to get parameters - {e}")
        response = flask.jsonify({"body": "Invalid parameters"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    logMessage = {
        "modelName": modelName,
        "imageNames": imageNames,
        "typeToIdentify": typeToIdentify,
        "responseIndex": responseIndex,
        "emotion": emotion
    }
    f = open("metrics.txt", "a")
    f.write(f"{json.dumps(logMessage)}\n")
    f.close()

    response = flask.jsonify({"body": "Successfully logged metric."})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


if __name__ == "__main__":
    app.run(port=5002)