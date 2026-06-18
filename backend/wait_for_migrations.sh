#!/bin/sh
set -e

until python manage.py migrate --check >/dev/null 2>&1; do
  sleep 3
done

exec "$@"
