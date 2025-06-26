# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy everything to /app in container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Flask
ENV PYTHONUNBUFFERED=True

# Expose Cloud Run port
ENV PORT=8080

# Run the app
CMD ["python", "run_service.py"]
