web: gunicorn workplace_system.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120
release: python manage.py migrate
