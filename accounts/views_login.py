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
        
        # DEBUG: Log login attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt for username: {username}")
        
        # Authenticate user FIRST - don't check school domain before authentication
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            logger.info(f"Authentication successful for: {username}")
            
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
            messages.error(request, '❌ Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
