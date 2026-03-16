# School Management System

A comprehensive multi-tenant school management system built with Django, supporting various educational institutions from nursery to university level.

## Features

- **Multi-tenant Architecture**: Support for multiple schools in a single deployment
- **Role-based Access Control**: Admin, Director, Teachers, Accountants, HR, etc.
- **Student Management**: Enrollment, attendance, grades, and reports
- **Fee Management**: Payment tracking, receipts, and defaulter reports
- **Employee Management**: Staff records, attendance, and performance reviews
- **Academic Management**: Subjects, exams, grades, and report cards
- **Library Management**: Book tracking and borrowing system
- **Inventory Management**: Asset and supply tracking
- **Parent Portal**: Communication between parents and teachers

## Technology Stack

- **Backend**: Django 4.2.29
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Authentication**: Django Auth with custom user profiles
- **Deployment**: Render.com ready

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 18+ (for production)
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ssenkula-rivan/school.git
cd school
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Access the application at `http://localhost:8000`

## Production Deployment

### Database Setup

1. Create PostgreSQL database:
```bash
createdb workplace_management
```

2. Update DATABASE_URL in .env:
```
DATABASE_URL=postgresql://user:password@localhost:5432/workplace_management?sslmode=disable
```

### Environment Variables

Required environment variables:

- `DEBUG=False`
- `ENVIRONMENT=production`
- `SECRET_KEY=<your-secret-key>`
- `DATABASE_URL=<postgresql-url>`
- `ALLOWED_HOSTS=<your-domain>`
- `SYSADMIN_PASSWORD=<admin-password>`
- `DISABLE_SSL_REDIRECT=True` (for local production without SSL)

### Running in Production

1. Collect static files:
```bash
python manage.py collectstatic --noinput
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the server:
```bash
gunicorn workplace_system.wsgi:application
```

## Default Credentials

After initial setup, use these credentials:

- **Admin**: admin / Admin@123456
- **Accountant**: accountant / Admin@123456

**⚠️ Change these passwords immediately in production!**

## Project Structure

```
school/
├── accounts/          # User authentication and profiles
├── academics/         # Academic management (subjects, exams)
├── core/             # Core functionality and multi-tenancy
├── employees/        # Employee management
├── fees/             # Fee and payment management
├── inventory/        # Inventory and asset management
├── library/          # Library management
├── reports/          # Reporting system
├── subscriptions/    # Subscription management
├── templates/        # HTML templates
├── static/           # Static files (CSS, JS, images)
└── workplace_system/ # Main project settings
```

## Key Management Commands

```bash
# Create admin user
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@school.com', 'password')"

# Backup database
python manage.py backup_database

# Security audit
python manage.py security_audit

# Test email configuration
python manage.py test_email

# Generate secure keys
python manage.py generate_secure_keys
```

## Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- Role-based access control
- Audit logging
- Session security
- Multi-tenant data isolation

## Support

For issues and questions, please open an issue on GitHub.

## License

Proprietary - All rights reserved

## Contributors

- Rivan Ssenkula (@ssenkula-rivan)
