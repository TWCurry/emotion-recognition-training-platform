#!/bin/bash
# CI script to create images of application

# Take branch name and tag as parameters
branch=$1
tag=$2
if [ $# -ne 2 ]
  then
    echo "Missing branch name or image tag. Usage: bash CI.sh branchName imageTag"
    exit 1
fi

# Checkout git repo
git clone git@github.com:TWCurry/emotion-recognition-training-platform.git
cd emotion-recognition-training-platform
git checkout $branch

# Copy Dockerfile from DevOps dir to root of repo
cp DevOps/Dockerfile Dockerfile

# Build image
sudo docker build -t fer-api:$tag .

# Tag image
sudo docker tag fer-api:$tag localhost:5001/fer-api:$tag

# Push image to registry
sudo docker push localhost:5001/fer-api:$tag

# Remove locally cached images
sudo docker image remove fer-api:$tag
sudo docker image remove localhost:5001/fer-api:$tag
sudo docker image remove python

# Remove git repo
cd ../
rm -rf emotion-recognition-training-platform