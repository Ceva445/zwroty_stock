#!/bin/sh

set -e

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting app..."
exec gunicorn zwroty_stock.wsgi:application --bind 0.0.0.0:8000 --workers 3
