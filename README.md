# Neocafe

Neocafe is an innovative mobile application designed to automate the ordering process in cafes and restaurants. It enables users to place orders quickly, track their status in real-time, and receive notifications upon readiness. Neocafe supports various user roles: customers, administrators, waiters, and baristas.

## Installation

### Prerequisites
- Python 3.x
- Redis-server
- pip3

### Steps
1. Clone the repository:
    ```sh
    git clone https://github.com/mcstao/NeoCafe.git
    cd NeoCafe-Project
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip3 install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python3 manage.py createsuperuser
    ```

6. Run the app:
    ```sh
    python3 -m uvicorn config.asgi:application --reload
    ```

7. Open the app in your browser at [http://127.0.0.1:8000/api/swagger-ui/](http://127.0.0.1:8000/api/swagger-ui/).

## Technologies and Services

- **Python 3.8**: Backend development.
- **Django REST Framework**: Building APIs.
- **Redis**: Asynchronous task processing and data caching.
- **Cloudinary**: Media management.

## User Roles

- **Customer**: Register, edit profile, view menus, place orders, track status, receive notifications.
- **Administrator**: Create branches, menu items, add employees and stock items.
- **Waiter/Barista**: Process and fulfill orders.

## Using the API

### Overview
The API allows for actions like creating orders and updating profiles. It is RESTful with resource-oriented URLs, form-encoded request bodies, JSON responses, and standard HTTP codes.

### Authentication
API keys are used for authentication. Keep them secure and do not share publicly.

### Author
Adilet Anarbaev
