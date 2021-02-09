#!/bin/bash
# CD Pipeline to deploy application
# Take image tag as parameter
tag=$1
if [ $# -eq 0 ]
  then
    echo "Missing image tag."
    exit 1
fi

cd ../

echo -e """version: \"3.8\"
services:
  flask-app:
    image: eu.gcr.io/majestic-hybrid-301217/fer-api:${tag}
    ports:
      - \"5000:5000\"
""" > docker-compose.yml
sudo docker-compose up -d
rm docker-compose.yml