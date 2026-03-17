from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class CoreConfig(AppConfig):
    name = 'core'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """Initialize app - validate configuration after Django is ready"""
        # Only validate in production or when explicitly requested
        import os
        if os.environ.get('SKIP_CONFIG_VALIDATION') == 'true':
            return
            
        try:
            from workplace_system.env_config import EnvironmentConfig
            
            # Print configuration
            EnvironmentConfig.print_config()
            
            # Validate configuration
            errors, warnings = EnvironmentConfig.validate()
            
            # Print warnings
            if warnings:
                print("\n" + "⚠️ " * 20)
                print("CONFIGURATION WARNINGS:")
                print("⚠️ " * 20)
                for warning in warnings:
                    print(f"⚠️  {warning}")
                print("⚠️ " * 20 + "\n")
            
            # Handle errors
            if errors:
                print("\n" + "!" * 40)
                print("CONFIGURATION ERRORS:")
                print("!" * 40)
                for error in errors:
                    print(f"❌ {error}")
                print("!" * 40 + "\n")
                
                # Only raise in development - production should try to continue
                if not EnvironmentConfig.is_production():
                    raise ImproperlyConfigured(f"Configuration errors: {'; '.join(errors)}")
                else:
                    print("⚠️  Production mode: Continuing despite configuration errors")
                    
        except Exception as e:
            # Never let config validation break the app
            print(f"Warning: Configuration validation failed: {e}")
            if not os.environ.get('ENVIRONMENT', '').lower() == 'production':
                raise
