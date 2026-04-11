from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('accounts/', views.chart_of_accounts, name='account_list'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('receipts/', views.receipt_list, name='receipt_list'),
]
