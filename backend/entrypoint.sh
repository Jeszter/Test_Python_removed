#!/bin/sh
set -e

until python manage.py showmigrations >/dev/null 2>&1; do
  sleep 2
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
