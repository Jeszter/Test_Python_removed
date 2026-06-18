# SPA Comments

Single-page comments application with nested replies, CAPTCHA, WebSocket updates and file uploads.

## Stack

| Layer | Technology |
| --- | --- |
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| Cache and broker | Redis |
| Realtime | Django Channels |
| Background jobs | Celery, Celery Beat |
| Frontend | Vue 3, Vite, Pinia |
| Proxy | Nginx |
| Deployment | Docke|

## Features

- Nested comments with recursive rendering
- Sorting by user name, email and creation date
- Pagination with 25 root comments per page
- LIFO ordering by default
- Server-generated CAPTCHA
- Server-side and client-side validation
- Allowed HTML tags: `<a>`, `<i>`, `<strong>`, `<code>`
- HTML sanitization with a strict allowlist
- Image uploads in JPG, GIF and PNG formats
- Automatic image resize to 320x240 maximum size
- TXT uploads up to 100 KB
- File preview with a lightbox-style overlay
- Message preview without page reload
- Toolbar for inserting allowed HTML tags
- WebSocket updates for new comments and replies
- Redis cache and channel layer
- Celery task for expired CAPTCHA cleanup

## Quick start

### Run

```bash
docker compose up --build
```

Application URLs:

```text
Frontend: http://localhost
Backend API: http://localhost/api
Django admin: http://localhost/admin
```


## Project structure

```text
backend/
  comments/
    models.py
    serializers.py
    views.py
    consumers.py
    tasks.py
    utils.py
  config/
    settings.py
    urls.py
    asgi.py
    celery.py
frontend/
  src/
    components/
    store/
    api/
nginx/
  nginx.conf
docker-compose.yml
db_schema.sql
```

## API

| Method | URL | Description |
| --- | --- | --- |
| GET | `/api/comments/` | Root comments list |
| POST | `/api/comments/` | Create comment |
| GET | `/api/comments/?ordering=username` | Sort comments |
| GET | `/api/comments/?page=2` | Paginate comments |
| GET | `/api/comments/<id>/` | Comment details |
| POST | `/api/comments/preview/` | Preview comment text |
| GET | `/api/captcha/` | Generate CAPTCHA |
| POST | `/api/captcha/validate/` | Validate CAPTCHA |

## Environment variables

| Name | Default | Description |
| --- | --- | --- |
| `DEBUG` | `True` | Debug mode |
| `SECRET_KEY` | `dev-secret-key` | Django secret key |
| `POSTGRES_DB` | `comments_db` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_HOST` | `db` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hosts |

## Security

- XSS protection is implemented with allowed HTML tags, attribute validation and server-side sanitization.
- SQL injection protection is handled through Django ORM.
- CAPTCHA records are single-use and expire on the server.
- Uploaded images are validated by extension and image format. TXT attachments are validated by extension and size.
- Images are resized before storage when they exceed the allowed dimensions.
- IP address and User-Agent are stored with each comment.

