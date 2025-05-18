# NourrIR Flask Project

This is the NourrIR Flask application for educational, nutritional, and creative well-being.

## Setup

1. Copy `.env.example` to `.env` and set your environment variable values.
2. Install dependencies: `pip install -r requirements.txt`
3. For development: `python app.py` (no auto-reload).

## Production

- Build and start with Docker Compose:
  ```
  docker-compose build
  docker-compose up -d
  ```
- The application is served via Gunicorn; configuration in `gunicorn_config.py`.
- Health check endpoint: `GET /health` returns `{ "status": "ok" }`.