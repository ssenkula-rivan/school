"""
Custom logout view to track logout events
"""
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def custom_logout(request):
    """Custom logout view that tracks logout"""
    if request.user.is_authenticated:
        try:
            # Mark user as logged out
            user_profile = request.user.userprofile
            user_profile.is_currently_logged_in = False
            user_profile.save(update_fields=['is_currently_logged_in'])
            logger.info(f"User {request.user.username} logged out")
        except Exception as e:
            logger.warning(f"Could not update logout tracking: {e}")
        
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    
    return redirect('accounts:login')
