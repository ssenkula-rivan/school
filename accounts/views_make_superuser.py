"""
Web-based superuser creation for Render free tier (no shell access)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import os


@require_http_methods(["GET", "POST"])
def make_superuser_web(request):
    """
    Web interface to make a user a superuser
    Protected by SECRET_KEY verification
    """
    
    # Only allow in production with correct secret
    if request.method == 'GET':
        context = {
            'users': User.objects.all().values_list('username', flat=True)
        }
        return render(request, 'accounts/make_superuser.html', context)
    
    # POST request
    username = request.POST.get('username', '').strip()
    secret_key = request.POST.get('secret_key', '').strip()
    
    # Verify secret key
    expected_secret = os.environ.get('SECRET_KEY', '')
    if not expected_secret or secret_key != expected_secret:
        messages.error(request, 'Invalid secret key. Use your SECRET_KEY environment variable.')
        return redirect('accounts:make_superuser_web')
    
    if not username:
        messages.error(request, 'Username is required.')
        return redirect('accounts:make_superuser_web')
    
    try:
        user = User.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        messages.success(
            request,
            f' Success! User "{username}" is now a superuser with full admin access. '
            f'You can now log in to /admin/ with this account.'
        )
        
        # Log the action
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'User {username} was made superuser via web interface')
        
    except User.DoesNotExist:
        messages.error(request, f'User "{username}" does not exist.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('accounts:make_superuser_web')
