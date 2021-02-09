# Base Image
FROM python:3.7.9-slim-buster

# Set the working directory in the container
WORKDIR /code

# Copy source code
COPY AutoTraining/src .

# Update apt packages and instance dependencies for python packages
RUN apt update -y

# Install dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Startup command
CMD python3 trainModels.py