FROM python:3.11-slim

# don't buffer stdout/stderr, and don't write .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your app
COPY . .

EXPOSE 8080

# tell gunicorn to stay in /app so it finds your modules
CMD ["gunicorn", "--chdir", "/app", "--config", "gunicorn_config.py", "app:app"]
