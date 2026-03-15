from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Public pages
    path('plans/', views.plans_list, name='plans'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Subscription management
    path('dashboard/', views.subscription_dashboard, name='dashboard'),
    path('upgrade/', views.upgrade_plan, name='upgrade'),
    path('renew/', views.renew_subscription, name='renew'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    
    # Status pages
    path('suspended/', views.subscription_suspended, name='suspended'),
    path('expired/', views.subscription_expired, name='expired'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoices'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    
    # Payment webhooks
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/flutterwave/', views.flutterwave_webhook, name='flutterwave_webhook'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
