from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Main employee management
    path('', views.employee_dashboard, name='dashboard'),
    path('list/', views.employee_list, name='list'),
    path('create/', views.employee_create, name='create'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_edit, name='edit'),
    
    # Leave management
    path('leaves/', views.leave_requests, name='leave_requests'),
    path('leaves/approve/', views.leave_requests, name='leave_approve'),  # Same view, different name for HR
    path('leaves/<int:pk>/approve/', views.approve_leave, name='approve_leave_detail'),
    
    # Performance management
    path('reviews/', views.performance_reviews, name='performance_reviews'),
    
    # Attendance
    path('attendance/', views.attendance_view, name='attendance'),
    
    # Role-specific dashboards
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('director/dashboard/', views.director_dashboard, name='director_dashboard'),
    path('dos/dashboard/', views.dos_dashboard, name='dos_dashboard'),
    path('registrar/dashboard/', views.registrar_dashboard, name='registrar_dashboard'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('head-of-class/dashboard/', views.head_of_class_dashboard, name='head_of_class_dashboard'),
    path('security/dashboard/', views.security_dashboard, name='security_dashboard'),
    path('receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('nurse/dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    
    # Work submissions
    path('submit-work/', views.submit_work, name='submit_work'),
    path('review-submissions/', views.review_submissions, name='review_submissions'),
    path('review-submissions/<int:pk>/', views.review_submission_detail, name='review_submission_detail'),
    
    # API endpoints
    path('api/search/', views.employee_search_api, name='search_api'),
]