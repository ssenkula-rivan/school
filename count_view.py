"""
Temporary view to count schools - add to your URLs temporarily
"""
from django.http import JsonResponse
from core.models import School
from django.contrib.auth.models import User
from accounts.models import UserProfile

def school_count_api(request):
    """Return JSON with school count and stats"""
    try:
        schools = School.objects.all()
        school_count = schools.count()
        
        school_details = []
        for school in schools:
            school_details.append({
                'name': school.name,
                'code': school.code,
                'type': school.school_type,
                'active': school.is_active,
                'created': school.created_at.isoformat() if school.created_at else None
            })
        
        data = {
            'total_schools': school_count,
            'schools': school_details,
            'total_users': User.objects.count(),
            'user_profiles': UserProfile.objects.count(),
            'timestamp': '2026-03-22T18:43:00Z'
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
