from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
]
