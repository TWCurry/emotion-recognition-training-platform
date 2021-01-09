#!/bin/bash
git clone git@github.com:TWCurry/emotion-recognition-training-platform.git
cd emotion-recognition-training-platform
docker build -t fer-api -f CI/Dockerfile .