# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY setup.py .
COPY README.md .

# Copy the source code into the container
COPY src/ ./src/

# Install the project along with its dependencies
RUN pip install --no-cache-dir -e .

# Specify the command to run the application
CMD ["bash"]