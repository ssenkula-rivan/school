from django.contrib.auth import views as auth_views, authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from core.models import School

class CustomLoginView(auth_views.LoginView):
    """Custom login view that identifies school by email domain"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after login"""
        return reverse_lazy('accounts:dashboard')
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').lower().strip()
        password = request.POST.get('password', '')
        
        # DEBUG: Log login attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt for username: {username}")
        logger.info(f"Password provided: {'Yes' if password else 'No'}")
        
        # Validate inputs
        if not username:
            messages.error(request, '❌ Username or email is required.')
            return render(request, self.template_name, self.get_context_data())
        
        if not password:
            messages.error(request, '❌ Password is required.')
            return render(request, self.template_name, self.get_context_data())
        
        # Check if username is system administrator trigger
        if username in ['system administrator', 'sysadmin', 'system admin']:
            return redirect('accounts:sysadmin_login')
        
        # DEBUG: Check if user exists
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(username=username)
            logger.info(f"User found: {user_obj.username}, ID: {user_obj.id}")
            logger.info(f"User is active: {user_obj.is_active}")
            logger.info(f"User is staff: {user_obj.is_staff}")
            logger.info(f"User is superuser: {user_obj.is_superuser}")
        except User.DoesNotExist:
            logger.info(f"User not found by username: {username}")
            # Try by email
            try:
                user_obj = User.objects.get(email=username)
                logger.info(f"User found by email: {user_obj.username}")
                username = user_obj.username  # Use username for authentication
            except User.DoesNotExist:
                logger.info(f"User not found by email either: {username}")
                # User doesn't exist - let authentication fail gracefully
                user = None
        
        # Authenticate user ONLY if user exists
        if user is None:
            logger.info(f"User not found, skipping authentication for: {username}")
        else:
            logger.info(f"Attempting authentication with username: {username}")
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            logger.info(f"Authentication successful for: {username}")
            login(request, user)
            logger.info(f"User logged in via login()")
            
            # Now set school context - for admins, allow any school
            if user.is_superuser:
                # For superusers, get the first active school or create session
                try:
                    school = School.objects.filter(is_active=True).first()
                    if school:
                        request.session['school_id'] = school.id
                        request.session['school_name'] = school.name
                        logger.info(f"Superuser logged in with school: {school.name}")
                except School.DoesNotExist:
                    logger.warning("No schools found for superuser")
            elif hasattr(user, 'userprofile') and user.userprofile.school:
                # For school-specific admins, use their assigned school
                school = user.userprofile.school
                request.session['school_id'] = school.id
                request.session['school_name'] = school.name
                logger.info(f"School admin logged in with school: {school.name}")
            else:
                # For regular users, try to find school by email domain
                if user.email and '@' in user.email:
                    email_domain = user.email.split('@')[1]
                    try:
                        school = School.objects.get(email_domain=email_domain, is_active=True)
                        request.session['school_id'] = school.id
                        request.session['school_name'] = school.name
                        logger.info(f"User logged in with school from email domain: {school.name}")
                    except School.DoesNotExist:
                        # If no school found for domain, try to find any active school
                        try:
                            school = School.objects.filter(is_active=True).first()
                            if school:
                                request.session['school_id'] = school.id
                                request.session['school_name'] = school.name
                                logger.info(f"User logged in with fallback school: {school.name}")
                        except School.DoesNotExist:
                            logger.error("No schools found for user")
            
            messages.success(request, f'✅ Welcome {user.first_name or user.username}! You have been logged in successfully.')
            return redirect(self.get_success_url())
        else:
            # Authentication failed
            logger.error(f"Authentication failed for: {username}")
            logger.error(f"User object returned: {user}")
            
            # Check if user exists but password is wrong
            try:
                user_obj = User.objects.get(username=username)
                logger.error(f"User exists but authentication failed - likely wrong password")
                logger.error(f"User is active: {user_obj.is_active}")
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(email=username)
                    logger.error(f"User exists by email but authentication failed - likely wrong password")
                except User.DoesNotExist:
                    logger.error(f"User does not exist at all")
            
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
