from django.urls import path
from . import views
from accounts.decorators import can_manage_fees

app_name = 'fees'

urlpatterns = [
    # Dashboard
    path('', views.fees_dashboard, name='dashboard'),
    path('bursar/', views.bursar_dashboard, name='bursar_dashboard'),
    
    # Students - Protected
    path('students/', can_manage_fees(views.student_list), name='student_list'),
    path('students/add/', can_manage_fees(views.student_create), name='student_create'),
    path('students/<int:pk>/', can_manage_fees(views.student_detail), name='student_detail'),
    path('students/<int:pk>/edit/', can_manage_fees(views.student_edit), name='student_edit'),
    
    # Fee Structure - Protected
    path('structure/', can_manage_fees(views.fee_structure_list), name='fee_structure_list'),
    path('structure/add/', can_manage_fees(views.fee_structure_create), name='fee_structure_create'),
    path('structure/<int:pk>/edit/', can_manage_fees(views.fee_structure_edit), name='fee_structure_edit'),
    
    # Payments - Protected
    path('payments/', can_manage_fees(views.payment_list), name='payment_list'),
    path('payments/add/', can_manage_fees(views.payment_create), name='payment_create'),
    path('payments/<int:pk>/', can_manage_fees(views.payment_detail), name='payment_detail'),
    path('payments/<int:pk>/receipt/', can_manage_fees(views.payment_receipt), name='payment_receipt'),
    
    # Balances - Protected
    path('balances/', can_manage_fees(views.balance_list), name='balance_list'),
    path('balances/student/<int:student_id>/', can_manage_fees(views.student_balance), name='student_balance'),
    
    # Reports - Protected
    path('reports/', can_manage_fees(views.fee_reports), name='reports'),
    path('reports/defaulters/', can_manage_fees(views.defaulters_report), name='defaulters_report'),
]
