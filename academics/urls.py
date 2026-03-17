from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Placeholder - add actual academic URLs here
    path('', views.dashboard, name='dashboard'),
]