#!/bin/bash
# CI script to create images of application

# Take branch name and tag as parameters
branch=$1
tag=$2
modelName=$3
if [ $# -ne 3 ]
  then
    echo "Incorrect parameters. Usage: bash CI.sh branchName imageTag modelFileName"
    exit 1
fi

# Checkout git repo
git clone git@github.com:TWCurry/emotion-recognition-training-platform.git
cd emotion-recognition-training-platform
git checkout $branch

# Fetch model from GCP Storage
gsutil cp gs://tc-fer-application-models/$modelName ExternalAI/legoAI/API/model.zip

# Unzip model
mkdir ExternalAI/legoAI/API/model
unzip ExternalAI/legoAI/API/model.zip -d ExternalAI/legoAI/API/model
rm ExternalAI/legoAI/API/model.zip -f 

# Copy Dockerfile from DevOps dir to root of repo
cp ExternalAI/legoAI/deployment/Dockerfile Dockerfile

# Build image
sudo docker build -t lego-api:$tag .

# Tag image
sudo docker tag lego-api:$tag eu.gcr.io/majestic-hybrid-301217/lego-api:$tag

# Push image to registry
sudo docker push eu.gcr.io/majestic-hybrid-301217/lego-api:$tag

# Remove locally cached images
sudo docker image remove lego-api:$tag
sudo docker image remove eu.gcr.io/majestic-hybrid-301217/lego-api:$tag
sudo docker image remove python

# Remove git repo
cd ../
rm -rf emotion-recognition-training-platform