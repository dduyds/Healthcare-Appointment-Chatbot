# Base image with Python 3.10
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Rasa
RUN pip install --upgrade pip
RUN pip install rasa

# Install action server dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project files
COPY . /app
WORKDIR /app

# Install an HTTP server to serve index.html
# RUN pip install http-server

# Expose ports for Rasa (5005) and the action server (5055)
EXPOSE 5005 5055 8000

# Run Rasa server, action server, and HTTP server simultaneously
CMD rasa run --cors "*" & \
    rasa run actions & \
    python -m http.server 8000
