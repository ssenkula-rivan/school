# Production Deployment Guide

## Quick Start for Production

### 1. Prepare Environment

```bash
# Copy production environment template
cp .env.production .env

# Edit .env with your production values
nano .env

# Key values to update:
# - SECRET_KEY (generate new one)
# - ENVIRONMENT=production
# - DEBUG=False
# - ALLOWED_HOSTS
# - Database credentials
# - Email credentials
# - Payment gateway keys
```

### 2. Generate Secure SECRET_KEY

```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# Copy output and paste into .env
```

### 3. Database Setup

```bash
# For PostgreSQL (recommended for production)
# 1. Create database and user
sudo -u postgres psql
CREATE DATABASE school_management_prod;
CREATE USER postgres_user WITH PASSWORD 'secure-password';
ALTER ROLE postgres_user SET client_encoding TO 'utf8';
ALTER ROLE postgres_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres_user SET default_transaction_deferrable TO on;
ALTER ROLE postgres_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE school_management_prod TO postgres_user;
\q

# 2. Update .env with database credentials
# 3. Run migrations
python manage.py migrate
```

### 4. Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput

# Verify staticfiles directory created
ls -la staticfiles/
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 6. Test Configuration

```bash
# Run Django checks
python manage.py check

# Should show: System check identified no issues (0 silenced)
```

---

## Web Server Setup (Gunicorn + Nginx)

### Install Gunicorn

```bash
pip install gunicorn
```

### Create Gunicorn Service File

Create `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for School Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/workplace-management-system
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/run/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    workplace_system.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

### Configure Nginx

Create `/etc/nginx/sites-available/school-management`:

```nginx
upstream gunicorn {
    server unix:/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "same-origin" always;
    
    # Logging
    access_log /var/log/nginx/school_management_access.log;
    error_log /var/log/nginx/school_management_error.log;
    
    # Client upload size
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /path/to/workplace-management-system/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /path/to/workplace-management-system/media/;
        expires 7d;
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/school-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Redis Setup (Optional but Recommended)

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping
# Should return: PONG
```

---

## Backup Configuration

### Automated Daily Backups

Create `/usr/local/bin/backup-school-system.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/school-management"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="school_management_prod"
DB_USER="postgres_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/workplace-management-system/media/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add line for daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-school-system.sh >> /var/log/backups.log 2>&1
```

---

## Monitoring & Logging

### Application Logs

```bash
# View Gunicorn logs
sudo journalctl -u gunicorn -f

# View Nginx logs
sudo tail -f /var/log/nginx/school_management_error.log
```

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
```

---

## Troubleshooting

### Gunicorn Not Starting

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Test configuration
python manage.py check

# Run Gunicorn manually for debugging
gunicorn --bind 0.0.0.0:8000 workplace_system.wsgi:application
```

### Database Connection Issues

```bash
# Test database connection
python manage.py dbshell

# Check database status
sudo systemctl status postgresql

# View database logs
sudo tail -f /var/log/postgresql/postgresql.log
```

### Static Files Not Loading

```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check permissions
ls -la staticfiles/
sudo chown -R www-data:www-data staticfiles/
```

---

## Performance Optimization

### Database Optimization

```bash
# Analyze query performance
python manage.py shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Run your code
    pass

for query in context:
    print(query['sql'])
```

### Caching

- Enable Redis caching (USE_REDIS=True)
- Configure cache timeouts
- Monitor cache hit rates

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Run load test
ab -n 1000 -c 10 https://yourdomain.com/
```

---

## Security Hardening

### Firewall Configuration

```bash
# Install UFW
sudo apt install ufw

# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Create local configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Enable and start
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Maintenance

### Regular Tasks

- Daily: Check error logs
- Weekly: Verify backups
- Monthly: Update dependencies
- Quarterly: Security audit
- Annually: Full system review

### Update Procedure

```bash
# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## Support & Documentation

- Django Docs: https://docs.djangoproject.com/
- Gunicorn Docs: https://docs.gunicorn.org/
- Nginx Docs: https://nginx.org/en/docs/
- PostgreSQL Docs: https://www.postgresql.org/docs/
