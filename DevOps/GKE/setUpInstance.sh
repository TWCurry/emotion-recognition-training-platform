#!/bin/bash
# Bash script to set up instance running Debian 10 buster

# Install dependencies
sudo apt-get install docker git python3

# Set up registry
docker run -d -p 5001:5000 --name registry-test registry:2