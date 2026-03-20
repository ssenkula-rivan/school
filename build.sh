#!/bin/bash

# Render build script for School Management System
echo "🚀 Starting Render deployment build..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (only in development)
if [ "$ENVIRONMENT" != "production" ]; then
    echo "👤 Creating development superuser..."
    python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@school.local', 'admin123')
    print('Development superuser created: admin/admin123')
else:
    print('Development superuser already exists')
EOF
fi

echo "✅ Build completed successfully!"
