"""
School provisioning and subscription services - ENTERPRISE GRADE
"""
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class ProvisioningError(Exception):
    """Raised when school provisioning fails"""
    pass


class SchoolProvisioningService:
    """
    Automated school provisioning - ONE ATOMIC FLOW
    
    CRITICAL: All-or-nothing provisioning
    - Creates school
    - Creates trial subscription
    - Creates admin user
    - Initializes defaults
    - Sends onboarding email
    """
    
    @staticmethod
    @transaction.atomic
    def provision_school(school_data, admin_data, plan_slug='trial'):
        """
        Provision a new school with all required setup
        
        GUARANTEES:
        - All operations succeed or all fail
        - No partial provisioning
        - Admin user created with proper permissions
        - Trial subscription activated
        - Default data initialized
        
        Args:
            school_data: Dict with school info (name, code, email, phone, address, etc.)
            admin_data: Dict with admin info (username, email, first_name, last_name, password)
            plan_slug: Plan slug (default: 'trial')
        
        Returns:
            tuple: (school, user, subscription)
        
        Raises:
            ProvisioningError: If provisioning fails
        """
        from core.models import School, AcademicYear
        from accounts.models import UserProfile
        from .models import Plan, Subscription
        
        try:
            # 1. Validate plan exists
            try:
                plan = Plan.objects.get(slug=plan_slug, is_active=True)
            except Plan.DoesNotExist:
                raise ProvisioningError(f"Plan '{plan_slug}' not found or inactive")
            
            # 2. Validate school code is unique
            if School.objects.filter(code=school_data['code']).exists():
                raise ProvisioningError(
                    f"School code '{school_data['code']}' already exists"
                )
            
            # 3. Validate admin username/email is unique
            if User.objects.filter(username=admin_data['username']).exists():
                raise ProvisioningError(
                    f"Username '{admin_data['username']}' already exists"
                )
            
            if User.objects.filter(email=admin_data['email']).exists():
                raise ProvisioningError(
                    f"Email '{admin_data['email']}' already exists"
                )
            
            # 4. Create school
            today = date.today()
            school = School.objects.create(
                name=school_data['name'],
                code=school_data['code'],
                school_type=school_data.get('school_type', 'combined'),
                institution_type=school_data.get('institution_type', 'private'),
                email=school_data['email'],
                phone=school_data['phone'],
                address=school_data['address'],
                website=school_data.get('website', ''),
                is_active=True,
                subscription_start=today,
                subscription_end=today + timedelta(days=plan.trial_days),
                max_students=plan.max_students,
                max_staff=plan.max_staff,
                currency=school_data.get('currency', 'USD'),
                timezone=school_data.get('timezone', 'UTC')
            )
            
            logger.info(
                f"School created: {school.code}",
                extra={'school_id': school.id}
            )
            
            # 5. Create subscription
            trial_end = today + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None
            
            subscription = Subscription.objects.create(
                school=school,
                plan=plan,
                status='trial' if plan.trial_days > 0 else 'active',
                current_period_start=today,
                current_period_end=today + timedelta(days=30),  # First month
                trial_start=today if plan.trial_days > 0 else None,
                trial_end=trial_end
            )
            
            logger.info(
                f"Subscription created: {school.code} - {plan.name}",
                extra={
                    'school_id': school.id,
                    'subscription_id': subscription.id,
                    'trial_end': trial_end
                }
            )
            
            # 6. Create admin user
            user = User.objects.create_user(
                username=admin_data['username'],
                email=admin_data['email'],
                password=admin_data['password'],
                first_name=admin_data.get('first_name', ''),
                last_name=admin_data.get('last_name', ''),
                is_active=True
            )
            
            # 7. Create user profile
            UserProfile.objects.create(
                user=user,
                school=school,
                role='school_admin',
                phone=admin_data.get('phone', '')
            )
            
            logger.info(
                f"Admin user created: {user.username}",
                extra={
                    'school_id': school.id,
                    'user_id': user.id
                }
            )
            
            # 8. Initialize default academic year
            current_year = today.year
            AcademicYear._unfiltered.create(
                school=school,
                name=f"{current_year}/{current_year + 1}",
                start_date=date(current_year, 1, 1),
                end_date=date(current_year, 12, 31),
                is_current=True
            )
            
            logger.info(
                f"Default academic year created: {current_year}/{current_year + 1}",
                extra={'school_id': school.id}
            )
            
            # 9. Send onboarding email (async if Celery available)
            try:
                from .tasks import send_onboarding_email
                send_onboarding_email.delay(
                    user.email,
                    school.code,
                    admin_data['username'],
                    trial_end
                )
            except ImportError:
                # Celery not available - send synchronously
                SchoolProvisioningService._send_onboarding_email_sync(
                    user.email,
                    school.code,
                    admin_data['username'],
                    trial_end
                )
            
            logger.info(
                f"School provisioning complete: {school.code}",
                extra={
                    'school_id': school.id,
                    'user_id': user.id,
                    'subscription_id': subscription.id
                }
            )
            
            return school, user, subscription
            
        except Exception as e:
            logger.error(
                f"School provisioning failed: {e}",
                exc_info=True
            )
            raise ProvisioningError(f"Provisioning failed: {e}")
    
    @staticmethod
    def _send_onboarding_email_sync(email, school_code, username, trial_end):
        """Send onboarding email synchronously"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"Welcome to {settings.SITE_NAME}!"
        message = f"""
Welcome to {settings.SITE_NAME}!

Your school account has been created successfully.

School Code: {school_code}
Username: {username}
Login URL: {settings.SITE_URL}/accounts/login/

{"Trial Period: " + str(trial_end) if trial_end else ""}

Next Steps:
1. Log in to your account
2. Complete your school profile
3. Add teachers and staff
4. Import or add students
5. Configure fee structures

Need help? Contact us at {settings.SUPPORT_EMAIL}

Best regards,
The {settings.SITE_NAME} Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            logger.info(f"Onboarding email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send onboarding email: {e}")
    
    @staticmethod
    def generate_school_code(school_name):
        """Generate unique school code from name"""
        from core.models import School
        
        # Take first 3 letters of each word, uppercase
        words = school_name.split()
        code_base = ''.join(word[:3].upper() for word in words[:3])
        
        # Ensure uniqueness
        code = code_base
        counter = 1
        while School.objects.filter(code=code).exists():
            code = f"{code_base}{counter}"
            counter += 1
        
        return code
    
    @staticmethod
    def generate_admin_username(email):
        """Generate username from email"""
        return email.split('@')[0].lower()
    
    @staticmethod
    def generate_random_password(length=12):
        """Generate secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password


class SubscriptionService:
    """
    Subscription management service
    
    CRITICAL: Handles subscription lifecycle
    """
    
    @staticmethod
    @transaction.atomic
    def upgrade_plan(subscription, new_plan_slug):
        """
        Upgrade subscription to new plan
        
        Args:
            subscription: Subscription instance
            new_plan_slug: New plan slug
        
        Returns:
            Subscription: Updated subscription
        """
        from .models import Plan
        
        try:
            new_plan = Plan.objects.get(slug=new_plan_slug, is_active=True)
        except Plan.DoesNotExist:
            raise ValueError(f"Plan '{new_plan_slug}' not found")
        
        if new_plan.price <= subscription.plan.price:
            raise ValueError("Can only upgrade to higher-priced plan")
        
        old_plan = subscription.plan
        subscription.plan = new_plan
        subscription.save()
        
        # Update school limits
        subscription.school.max_students = new_plan.max_students
        subscription.school.max_staff = new_plan.max_staff
        subscription.school.save()
        
        logger.info(
            f"Plan upgraded: {subscription.school.code} from {old_plan.name} to {new_plan.name}",
            extra={
                'school_id': subscription.school.id,
                'old_plan': old_plan.name,
                'new_plan': new_plan.name
            }
        )
        
        return subscription
    
    @staticmethod
    @transaction.atomic
    def activate_subscription(subscription, external_payment_id=''):
        """
        Activate subscription after payment
        
        Args:
            subscription: Subscription instance
            external_payment_id: Payment gateway subscription ID
        """
        subscription.status = 'active'
        subscription.external_payment_id = external_payment_id
        subscription.save()
        
        logger.info(
            f"Subscription activated: {subscription.school.code}",
            extra={
                'school_id': subscription.school.id,
                'external_payment_id': external_payment_id
            }
        )
    
    @staticmethod
    def check_expiring_subscriptions(days=7):
        """
        Get subscriptions expiring in N days
        
        Returns:
            QuerySet: Expiring subscriptions
        """
        from .models import Subscription
        
        expiry_date = date.today() + timedelta(days=days)
        
        return Subscription.objects.filter(
            status='active',
            current_period_end__lte=expiry_date,
            current_period_end__gte=date.today()
        ).select_related('school', 'plan')
    
    @staticmethod
    @transaction.atomic
    def suspend_expired_subscriptions():
        """
        Suspend all expired subscriptions
        
        Returns:
            int: Number of subscriptions suspended
        """
        from .models import Subscription
        
        expired = Subscription.objects.filter(
            status='active',
            current_period_end__lt=date.today()
        )
        
        count = 0
        for subscription in expired:
            subscription.suspend(reason='Payment overdue')
            count += 1
        
        logger.info(f"Suspended {count} expired subscriptions")
        return count
