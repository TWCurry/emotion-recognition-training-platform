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
  lego-app:
    image: localhost:5001/lego-api:${tag}
    ports:
      - \"5002:5000\"
""" > docker-compose.yml
sudo docker-compose up -d
rm docker-compose.yml