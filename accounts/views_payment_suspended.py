"""
Payment Suspended View
Shows notification when school account is blocked for non-payment
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def payment_suspended(request):
    """
    Show payment suspended notification page
    Displayed when school is blocked for non-payment
    """
    school = None
    
    # Try to get school from request
    if hasattr(request, 'school'):
        school = request.school
    elif hasattr(request.user, 'userprofile') and request.user.userprofile.school:
        school = request.user.userprofile.school
    
    context = {
        'school': school,
    }
    
    return render(request, 'accounts/payment_suspended.html', context)
