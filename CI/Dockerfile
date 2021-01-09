# Base Image
FROM python:3.7.9-slim-buster

# Set the working directory in the container
WORKDIR /code

# Copy source code
COPY API/ .

# Update apt packages and instance dependencies for python packages
RUN apt update -y
RUN apt install libgl1-mesa-glx libglib2.0-0 -y

# Install dependencies
RUN pip install -r requirements.txt

# Install tflite
RUN pip install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp37-cp37m-linux_x86_64.whl

# Startup command
CMD [ "python", "./api.py" ]