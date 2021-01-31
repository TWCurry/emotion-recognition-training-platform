# Base Image
FROM python:3.7.9-slim-buster

# Set the working directory in the container
WORKDIR /code

# Copy source code
COPY ExternalAi/API/ .

# Update apt packages and instance dependencies for python packages
RUN apt update -y

# Install dependencies
RUN pip install -r requirements.txt

# Setup Flask environment variables
ENV FLASK_APP=api.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000
EXPOSE 5000

# Startup command
CMD [ "flask", "run" ]