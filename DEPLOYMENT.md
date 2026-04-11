# Deployment Guide - Fly.io

## Prerequisites
1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Sign up for Fly.io account
3. Login: `flyctl auth login`

## Initial Setup

### 1. Create Fly.io App
```bash
flyctl launch --no-deploy
```

### 2. Create PostgreSQL Database
```bash
flyctl postgres create --name school-management-db --region iad
flyctl postgres attach school-management-db
```

### 3. Set Environment Variables
```bash
flyctl secrets set SECRET_KEY="your-secret-key-here"
flyctl secrets set DEBUG="False"
flyctl secrets set ALLOWED_HOSTS="your-app.fly.dev"
```

### 4. Deploy
```bash
flyctl deploy
```

### 5. Run Migrations
```bash
flyctl ssh console
python manage.py migrate
python manage.py createsuperuser
exit
```

## Access Your App
```bash
flyctl open
```

Your app will be available at: https://your-app.fly.dev

## Monitoring
```bash
# View logs
flyctl logs

# Check status
flyctl status

# SSH into app
flyctl ssh console
```

## Scaling
```bash
# Scale to 2 instances
flyctl scale count 2

# Scale memory
flyctl scale memory 512
```

## Database Backup
```bash
flyctl postgres backup list -a school-management-db
flyctl postgres backup create -a school-management-db
```

## Troubleshooting
```bash
# View recent logs
flyctl logs --app your-app-name

# Restart app
flyctl apps restart your-app-name

# Check health
flyctl checks list
```
