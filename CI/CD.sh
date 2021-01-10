#!/bin/bash
cp Dockerfile ../Dockerfile
cp docker-compose.yml ../docker-compose.yml
cd ../
docker-compose up -d