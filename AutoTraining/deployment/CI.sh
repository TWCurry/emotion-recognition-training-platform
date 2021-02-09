#!/bin/bash
# CI script to create images of application

# Checkout git repo
git clone git@github.com:TWCurry/emotion-recognition-training-platform.git
cd emotion-recognition-training-platform
git checkout dev

# Copy Dockerfile from DevOps dir to root of repo
cp AutoTraining/deployment/Dockerfile Dockerfile

# Build image
sudo docker build -t model-trainer:latest .

# Tag image
sudo docker tag model-trainer:latest localhost:5001/model-trainer:latest

# Push image to registry
sudo docker push localhost:5001/model-trainer:latest

# Remove locally cached images
sudo docker image remove model-trainer:latest
sudo docker image remove localhost:5001/model-trainer:latest

# Remove git repo
cd ../
rm -rf emotion-recognition-training-platform