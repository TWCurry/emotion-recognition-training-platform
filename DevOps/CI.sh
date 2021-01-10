#!/bin/bash
# CI script to create images of application

# Take branch name as parameter
branch=$1
if [ $# -eq 0 ]
  then
    echo "Missing branch name."
    exit 1
fi

# Checkout git repo
git clone git@github.com:TWCurry/emotion-recognition-training-platform.git
cd emotion-recognition-training-platform
git checkout $branch

# Copy Dockerfile from DevOps dir to root of repo
cp DevOps/Dockerfile Dockerfile

# Build image
sudo docker build -t fer-api:latest .

# Tag image
sudo docker tag fer-api:latest localhost:5001/fer-api

# Push image to registry
sudo docker push localhost:5001/fer-api

# Remove locally cached images
sudo docker image remove fer-api:latest
sudo docker image remove localhost:5001/fer-api

# Remove git repo
cd ../
rm -rf emotion-recognition-training-platform