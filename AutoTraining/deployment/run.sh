#!/bin/bash

# Deploy container
sudo docker-compose up -d

# Delete container once it's finished
sudo docker stop deployment_model-trainer_1
sudo docker rm deployment_model-trainer_1