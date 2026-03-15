"""
Subscription and feature decorators - ENTERPRISE GRADE
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import FeatureNotAllowed, PlanLimitExceeded
import logging

logger = logging.getLogger(__name__)


def subscription_required(view_func):
    """
    Require active subscription to access view
    
    Usage:
        @subscription_required
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'school') or not request.school:
            messages.error(request, 'No school context found')
            return redirect('accounts:login')
        
        if not hasattr(request.school, 'subscription'):
            messages.error(request, 'No subscription found for this school')
            return redirect('subscriptions:subscribe')
        
        subscription = request.school.subscription
        
        if not subscription.is_active:
            if subscription.status == 'expired':
                messages.error(request, 'Your subscription has expired. Please renew to continue.')
                return redirect('subscriptions:renew')
            elif subscription.status == 'suspended':
                messages.error(request, 'Your subscription is suspended. Please contact support.')
                return redirect('subscriptions:suspended')
            elif subscription.status == 'cancelled':
                messages.error(request, 'Your subscription has been cancelled.')
                return redirect('subscriptions:subscribe')
            else:
                messages.error(request, 'Your subscription is not active.')
                return redirect('subscriptions:subscribe')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_feature(feature_name):
    """
    Require specific feature to access view
    
    Usage:
        @require_feature('advanced_reports')
        def advanced_reports_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'school') or not request.school:
                messages.error(request, 'No school context found')
                return redirect('accounts:login')
            
            if not hasattr(request.school, 'subscription'):
                messages.error(request, 'No subscription found')
                return redirect('subscriptions:subscribe')
            
            subscription = request.school.subscription
            
            if not subscription.has_feature(feature_name):
                logger.warning(
                    f"Feature access denied: {feature_name}",
                    extra={
                        'school_id': request.school.id,
                        'plan': subscription.plan.name,
                        'feature': feature_name
                    }
                )
                messages.error(
                    request,
                    f"This feature is not available in your {subscription.plan.name} plan. "
                    f"Please upgrade to access {feature_name.replace('_', ' ').title()}."
                )
                return redirect('subscriptions:upgrade')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def check_student_limit(view_func):
    """
    Check student limit before allowing student creation
    
    Usage:
        @check_student_limit
        def create_student_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            if hasattr(request, 'school') and hasattr(request.school, 'subscription'):
                try:
                    request.school.subscription.check_student_limit()
                except PlanLimitExceeded as e:
                    logger.warning(
                        f"Student limit exceeded: {request.school.code}",
                        extra={'school_id': request.school.id}
                    )
                    messages.error(request, str(e))
                    return redirect('subscriptions:upgrade')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_staff_limit(view_func):
    """
    Check staff limit before allowing staff creation
    
    Usage:
        @check_staff_limit
        def create_staff_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            if hasattr(request, 'school') and hasattr(request.school, 'subscription'):
                try:
                    request.school.subscription.check_staff_limit()
                except PlanLimitExceeded as e:
                    logger.warning(
                        f"Staff limit exceeded: {request.school.code}",
                        extra={'school_id': request.school.id}
                    )
                    messages.error(request, str(e))
                    return redirect('subscriptions:upgrade')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def trial_allowed(view_func):
    """
    Allow access during trial period
    
    Usage:
        @trial_allowed
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'school') or not request.school:
            messages.error(request, 'No school context found')
            return redirect('accounts:login')
        
        if not hasattr(request.school, 'subscription'):
            messages.error(request, 'No subscription found')
            return redirect('subscriptions:subscribe')
        
        subscription = request.school.subscription
        
        # Allow if active OR in trial
        if not (subscription.is_active or subscription.is_trial):
            messages.error(request, 'Your trial has expired. Please subscribe to continue.')
            return redirect('subscriptions:subscribe')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
