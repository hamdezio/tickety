# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your app files into the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5002

# Set an environment variable for Flask app (optional but good practice)
ENV FLASK_APP=app.py

# Command to run your Flask app
CMD ["python", "app.py"]
