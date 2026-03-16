# Deployment Guide

## Quick Deployment Checklist

### 1. Environment Setup

Create a `.env` file with these required variables:

```env
# Django Settings
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<generate-a-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# System Admin
SYSADMIN_PASSWORD=<strong-password>

# For local production without SSL
DISABLE_SSL_REDIRECT=True

# Company Information
COMPANY_NAME=Your School Name
COMPANY_EMAIL=admin@yourschool.com
COMPANY_ADDRESS=Your School Address
COMPANY_PHONE=+1-234-567-8900

# Email Configuration (Optional but recommended)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourschool.com
```

### 2. Database Setup

#### PostgreSQL (Recommended for Production)

```bash
# Create database
createdb workplace_management

# Or using psql
psql -U postgres
CREATE DATABASE workplace_management;
\q
```

#### Update DATABASE_URL

For local PostgreSQL without SSL:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/workplace_management?sslmode=disable
```

For remote PostgreSQL with SSL:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

### 3. Initial Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 4. Configure School

After first login as superuser, the system will prompt you to configure your school. Or run:

```bash
python manage.py shell -c "
from accounts.models import SchoolConfiguration
school = SchoolConfiguration.objects.create(
    school_name='Your School Name',
    school_type='secondary',  # or primary, nursery, college, university
    institution_type='private',
    address='School Address',
    phone='+1-234-567-8900',
    email='admin@school.com',
    is_configured=True
)
print('School configured successfully!')
"
```

### 5. Create Initial Users

```bash
# Create admin user
python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import UserProfile

user = User.objects.create_superuser('admin', 'admin@school.com', 'Admin@123456')
profile = UserProfile.objects.create(
    user=user,
    employee_id='ADMIN001',
    role='admin'
)
print('Admin user created')
"

# Create accountant user
python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import UserProfile

user = User.objects.create_user('accountant', 'accountant@school.com', 'Admin@123456')
user.is_staff = True
user.save()
profile = UserProfile.objects.create(
    user=user,
    employee_id='ACC001',
    role='accountant'
)
print('Accountant user created')
"
```

### 6. Run the Server

#### Development
```bash
python manage.py runserver
```

#### Production (with Gunicorn)
```bash
gunicorn workplace_system.wsgi:application --bind 0.0.0.0:8000
```

## Deployment Platforms

### Render.com

1. Connect your GitHub repository
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy!

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SYSADMIN_PASSWORD=your-password

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### DigitalOcean / AWS / VPS

1. Set up Ubuntu server
2. Install Python, PostgreSQL, Nginx
3. Clone repository
4. Set up virtual environment
5. Configure Nginx as reverse proxy
6. Use systemd for process management
7. Set up SSL with Let's Encrypt

## Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure firewall
- [ ] Set up database backups
- [ ] Enable audit logging
- [ ] Configure email notifications
- [ ] Set up monitoring
- [ ] Regular security updates

## Troubleshooting

### CSRF Errors
- Ensure CSRF_TRUSTED_ORIGINS includes your domain
- Check SECURE_SSL_REDIRECT settings
- Clear browser cookies

### Redirect Loop
- Verify school is configured: `is_configured=True`
- Check DISABLE_SSL_REDIRECT for local production

### Database Connection Errors
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Verify credentials and permissions
- Check SSL mode settings

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings
- Verify Whitenoise is in MIDDLEWARE

## Maintenance

### Backup Database
```bash
python manage.py backup_database
```

### Security Audit
```bash
python manage.py security_audit
```

### Test Email
```bash
python manage.py test_email
```

## Support

For issues, contact: admin@yourschool.com
