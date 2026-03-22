#!/bin/bash

echo "============================================================"
echo "SCHOOL MANAGEMENT SYSTEM - DATABASE STATUS"
echo "============================================================"

# Check if we can access the database via Django management
echo "🔍 Checking database access..."
cd /home/cranictech/CascadeProjects/school

# Try to run Django management commands
echo ""
echo "📊 Django Management Commands Status:"
echo "----------------------------------------"

# Check migrations
echo "🗄️  Checking migrations:"
python3 manage.py showmigrations --plan 2>/dev/null | head -20

echo ""
echo "👥 Checking users:"
python3 manage.py shell -c "
from django.contrib.auth.models import User
count = User.objects.count()
print(f'  Total Users: {count}')
if count > 0:
    for user in User.objects.all()[:5]:
        print(f'  - {user.username} ({user.email})')
if count > 5:
    print(f'  ... and {count-5} more users')
" 2>/dev/null

echo ""
echo "🏫 Checking schools:"
python3 manage.py shell -c "
from core.models import School
count = School.objects.count()
print(f'  Total Schools: {count}')
if count > 0:
    for school in School.objects.all()[:5]:
        print(f'  - {school.name} ({school.school_type})')
if count > 5:
    print(f'  ... and {count-5} more schools')
" 2>/dev/null

echo ""
echo "⚙️  Checking school configurations:"
python3 manage.py shell -c "
from accounts.models import SchoolConfiguration
count = SchoolConfiguration.objects.count()
print(f'  Total Configurations: {count}')
if count > 0:
    for config in SchoolConfiguration.objects.all()[:5]:
        print(f'  - {config.school_name} ({config.school_type})')
if count > 5:
    print(f'  ... and {count-5} more configurations')
" 2>/dev/null

echo ""
echo "============================================================"
echo "If you see errors above, the database connection is failing"
echo "============================================================"
