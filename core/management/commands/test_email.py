"""
Management command to test email configuration
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('EMAIL CONFIGURATION TEST'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Display configuration
        self.stdout.write('Configuration:')
        self.stdout.write(f'  Email Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  Email Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'  Email Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'  Email Use TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  Email Use SSL: {settings.EMAIL_USE_SSL}')
        self.stdout.write(f'  Email User: {settings.EMAIL_HOST_USER or "NOT SET"}')
        self.stdout.write(f'  Email Password: {"SET" if settings.EMAIL_HOST_PASSWORD else "NOT SET"}')
        self.stdout.write(f'  Default From Email: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write()
        
        # Check if credentials are set
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(self.style.WARNING('  WARNING: Email credentials not configured'))
            self.stdout.write(self.style.WARNING('   EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are empty'))
            self.stdout.write(self.style.WARNING('   Email sending will use console backend (development mode)'))
            self.stdout.write()
            
            if 'console' in settings.EMAIL_BACKEND:
                self.stdout.write(self.style.SUCCESS(' Console backend active (development mode)'))
                self.stdout.write(self.style.SUCCESS('   Emails will be printed to console instead of sent'))
                self.stdout.write()
                
                # Test console backend
                try:
                    send_mail(
                        subject='Test Email - Password Reset',
                        message='This is a test email to verify password reset functionality.\n\nPassword Reset Link: https://example.com/accounts/password-reset/token/',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['test@example.com'],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(' SUCCESS: Test email sent to console'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f' ERROR: {str(e)}'))
            else:
                self.stdout.write(self.style.ERROR(' ERROR: SMTP backend configured but credentials missing'))
                self.stdout.write(self.style.ERROR('   Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env'))
        else:
            # Test SMTP
            self.stdout.write(self.style.SUCCESS(' Email credentials configured'))
            self.stdout.write()
            
            try:
                self.stdout.write('Testing SMTP connection...')
                send_mail(
                    subject='Test Email - Password Reset',
                    message='This is a test email to verify password reset functionality.\n\nPassword Reset Link: https://example.com/accounts/password-reset/token/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['test@example.com'],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(' SUCCESS: Test email sent successfully'))
                self.stdout.write(self.style.SUCCESS('   Email configuration is working correctly'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f' ERROR: {str(e)}'))
                self.stdout.write(self.style.ERROR('   Check your email credentials and SMTP settings'))
        
        self.stdout.write()
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('For production, configure in .env:'))
        self.stdout.write(self.style.WARNING('  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend'))
        self.stdout.write(self.style.WARNING('  EMAIL_HOST=smtp.gmail.com'))
        self.stdout.write(self.style.WARNING('  EMAIL_PORT=587'))
        self.stdout.write(self.style.WARNING('  EMAIL_USE_TLS=True'))
        self.stdout.write(self.style.WARNING('  EMAIL_HOST_USER=your-email@gmail.com'))
        self.stdout.write(self.style.WARNING('  EMAIL_HOST_PASSWORD=your-app-password'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
