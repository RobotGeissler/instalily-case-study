# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy code and environment files
COPY ./backend /app
COPY requirements.txt /app
COPY .env /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the Flask app
CMD ["python", "app.py"]
