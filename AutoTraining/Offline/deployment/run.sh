#!/bin/bash

# Deploy container
echo "============== Deploying Container... =============="
sudo docker-compose up -d

# View logs
echo "============== Container Logs =============="
sudo docker logs -f deployment_model-trainer_1

# Delete container once it's finished
echo "============== Deleting Container... =============="
sudo docker stop deployment_model-trainer_1
sudo docker rm deployment_model-trainer_1