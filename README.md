# Vehicle Detection API

This project is a FastAPI-based web application for vehicle detection in images. It uses a pre-trained Faster R-CNN model to detect various types of vehicles and provides a web interface for uploading images and viewing detection results.

## Features

- User registration and authentication
- Image upload and vehicle detection
- Viewing detection history
- Celery for asynchronous task processing
- Redis for task queue management
- SQLAlchemy for database interactions

## Requirements

- Docker
- Docker Compose

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/vehicle-detection-api.git
    cd vehicle-detection-api
    ```

2. Build and start the Docker containers:

    ```bash
    docker-compose up --build
    ```

3. The application will be available at `http://localhost:8000`.

## Configuration

The application configuration is defined in the `app/core/config.py` file. You can modify the configuration values directly in this file.

### Example Configuration
