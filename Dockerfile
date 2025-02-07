# Dockerfile

# Use a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run the application (replace with your app's entrypoint)
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
