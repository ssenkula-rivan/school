from django.contrib.auth import views as auth_views, authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from core.models import School

class CustomLoginView(auth_views.LoginView):
    """Custom login view that identifies school by email domain"""
    
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
        
        # Check if username is an email - identify school by domain
        if '@' in username:
            email_domain = username.split('@')[1]
            try:
                school = School.objects.get(email_domain=email_domain, is_active=True)
                # Store school in session for tenant middleware
                request.session['school_id'] = school.id
                request.session['school_name'] = school.name
                messages.info(request, f'🏫 Logging into {school.name}')
            except School.DoesNotExist:
                messages.error(request, f'❌ No active school found for email domain: @{email_domain}. Please contact your administrator.')
                return render(request, self.template_name, self.get_context_data())
        
        # Attempt authentication
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            # Generic error to avoid leaking which usernames exist
            messages.error(request, '❌ Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
        
        # Proceed with normal login
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """After successful login, ensure school context is set"""
        response = super().form_valid(form)
        
        # If user has email, try to set school from email domain
        user = form.get_user()
        if user.email and '@' in user.email:
            email_domain = user.email.split('@')[1]
            try:
                school = School.objects.get(email_domain=email_domain, is_active=True)
                self.request.session['school_id'] = school.id
                self.request.session['school_name'] = school.name
            except School.DoesNotExist:
                pass
        
        messages.success(request, f'✅ Welcome {user.first_name or user.username}! You have been logged in successfully.')
        return response
