# Use an official Python runtime as a parent image
FROM python:3.14-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in pyproject.toml
# We need a tool to install from pyproject.toml, like pip or poetry. 
# Assuming standard pip for now, but pyproject.toml usually implies a build system.
# For simplicity in this initialization, we'll just upgrade pip and install .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Run the application
CMD ["python", "main.py"]
