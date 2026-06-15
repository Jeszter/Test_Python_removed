version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: comments_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    command: sh entrypoint.sh
    volumes:
      - ./backend:/app
      - media_data:/app/media
    environment:
      DEBUG: "False"
      SECRET_KEY: "change-me-in-production-please"
      POSTGRES_DB: comments_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      REDIS_URL: redis://redis:6379/0
      ALLOWED_HOSTS: "localhost,127.0.0.1,backend"
      CORS_ALLOWED_ORIGINS: "http://localhost,http://localhost:80,http://frontend"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "python manage.py showmigrations comments | grep -q '\\[X\\]'"]
      interval: 5s
      timeout: 10s
      retries: 10
      start_period: 20s

  celery:
    build: ./backend
    command: sh wait_for_migrations.sh celery -A config.celery worker -l info
    volumes:
      - ./backend:/app
      - media_data:/app/media
    environment:
      DEBUG: "False"
      SECRET_KEY: "change-me-in-production-please"
      POSTGRES_DB: comments_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_healthy

  celery-beat:
    build: ./backend
    command: sh wait_for_migrations.sh celery -A config.celery beat -l info
    volumes:
      - ./backend:/app
    environment:
      DEBUG: "False"
      SECRET_KEY: "change-me-in-production-please"
      POSTGRES_DB: comments_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_healthy

  frontend:
    build: ./frontend
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - media_data:/app/media:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  media_data:
