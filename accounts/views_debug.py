from django.http import JsonResponse
from accounts.school_config import SchoolConfiguration


def debug_config(request):
    """Debug endpoint to check school configuration status"""
    try:
        config = SchoolConfiguration.get_config()
        is_configured = SchoolConfiguration.is_school_configured()
        
        return JsonResponse({
            'config_exists': config is not None,
            'is_configured': is_configured,
            'config_data': {
                'school_name': config.school_name if config else None,
                'school_type': config.school_type if config else None,
                'is_configured': config.is_configured if config else None,
            } if config else None
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'config_exists': False,
            'is_configured': False
        })
