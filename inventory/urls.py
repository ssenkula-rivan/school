from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Placeholder - add actual inventory URLs here
    path('', views.dashboard, name='dashboard'),
]