"""
Subscription views - ENTERPRISE GRADE
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Plan, Subscription, SubscriptionInvoice
from .services import SubscriptionService
import logging

logger = logging.getLogger(__name__)


def plans_list(request):
    """Public pricing page"""
    plans = Plan.objects.filter(is_active=True, is_public=True).order_by('sort_order', 'price')
    
    context = {
        'plans': plans,
    }
    return render(request, 'subscriptions/plans.html', context)


@login_required
def subscribe(request):
    """Subscribe to a plan"""
    if request.method == 'POST':
        plan_slug = request.POST.get('plan')
        
        try:
            plan = Plan.objects.get(slug=plan_slug, is_active=True)
        except Plan.DoesNotExist:
            messages.error(request, 'Invalid plan selected')
            return redirect('subscriptions:plans')
        
        # TODO: Integrate with payment gateway
        # For now, just show message
        messages.info(
            request,
            f'Payment integration coming soon. Selected plan: {plan.name}'
        )
        return redirect('subscriptions:dashboard')
    
    plans = Plan.objects.filter(is_active=True, is_public=True)
    return render(request, 'subscriptions/subscribe.html', {'plans': plans})


@login_required
def subscription_dashboard(request):
    """Subscription dashboard"""
    if not hasattr(request, 'school') or not request.school:
        messages.error(request, 'No school context found')
        return redirect('accounts:login')
    
    try:
        subscription = request.school.subscription
    except Subscription.DoesNotExist:
        messages.warning(request, 'No subscription found. Please subscribe.')
        return redirect('subscriptions:subscribe')
    
    # Get recent invoices
    invoices = subscription.invoices.all()[:10]
    
    context = {
        'subscription': subscription,
        'invoices': invoices,
    }
    return render(request, 'subscriptions/dashboard.html', context)


@login_required
def upgrade_plan(request):
    """Upgrade to higher plan"""
    if not hasattr(request, 'school') or not request.school:
        messages.error(request, 'No school context found')
        return redirect('accounts:login')
    
    try:
        subscription = request.school.subscription
    except Subscription.DoesNotExist:
        messages.error(request, 'No subscription found')
        return redirect('subscriptions:subscribe')
    
    if request.method == 'POST':
        new_plan_slug = request.POST.get('plan')
        
        try:
            SubscriptionService.upgrade_plan(subscription, new_plan_slug)
            messages.success(request, 'Plan upgraded successfully!')
            return redirect('subscriptions:dashboard')
        except Exception as e:
            messages.error(request, str(e))
    
    # Get plans higher than current
    available_plans = Plan.objects.filter(
        is_active=True,
        price__gt=subscription.plan.price
    ).order_by('price')
    
    context = {
        'subscription': subscription,
        'available_plans': available_plans,
    }
    return render(request, 'subscriptions/upgrade.html', context)


@login_required
def renew_subscription(request):
    """Renew expired subscription"""
    if not hasattr(request, 'school') or not request.school:
        messages.error(request, 'No school context found')
        return redirect('accounts:login')
    
    try:
        subscription = request.school.subscription
    except Subscription.DoesNotExist:
        messages.error(request, 'No subscription found')
        return redirect('subscriptions:subscribe')
    
    # TODO: Integrate with payment gateway
    messages.info(request, 'Payment integration coming soon')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'subscriptions/renew.html', context)


@login_required
@require_POST
def cancel_subscription(request):
    """Cancel subscription"""
    if not hasattr(request, 'school') or not request.school:
        messages.error(request, 'No school context found')
        return redirect('accounts:login')
    
    try:
        subscription = request.school.subscription
    except Subscription.DoesNotExist:
        messages.error(request, 'No subscription found')
        return redirect('subscriptions:dashboard')
    
    reason = request.POST.get('reason', '')
    immediate = request.POST.get('immediate') == 'true'
    
    subscription.cancel(reason=reason, immediate=immediate)
    
    if immediate:
        messages.warning(request, 'Subscription cancelled immediately')
    else:
        messages.info(request, 'Subscription will be cancelled at end of billing period')
    
    return redirect('subscriptions:dashboard')


def subscription_suspended(request):
    """Subscription suspended page"""
    return render(request, 'subscriptions/suspended.html')


def subscription_expired(request):
    """Subscription expired page"""
    return render(request, 'subscriptions/expired.html')


@login_required
def invoice_list(request):
    """List all invoices"""
    if not hasattr(request, 'school') or not request.school:
        messages.error(request, 'No school context found')
        return redirect('accounts:login')
    
    try:
        subscription = request.school.subscription
        invoices = subscription.invoices.all()
    except Subscription.DoesNotExist:
        invoices = []
    
    return render(request, 'subscriptions/invoices.html', {'invoices': invoices})


@login_required
def invoice_detail(request, invoice_id):
    """Invoice detail"""
    invoice = get_object_or_404(SubscriptionInvoice, id=invoice_id)
    
    # Verify invoice belongs to user's school
    if hasattr(request, 'school') and invoice.subscription.school != request.school:
        messages.error(request, 'Access denied')
        return redirect('subscriptions:invoices')
    
    return render(request, 'subscriptions/invoice_detail.html', {'invoice': invoice})


# ============================================================================
# PAYMENT GATEWAY WEBHOOKS
# ============================================================================

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe webhook handler
    
    CRITICAL: Verify webhook signature before processing
    """
    import stripe
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Stripe webhook: Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Stripe webhook: Invalid signature")
        return HttpResponse(status=400)
    
    # Handle event
    if event['type'] == 'invoice.payment_succeeded':
        # Payment successful - activate subscription
        logger.info(f"Stripe payment succeeded: {event['id']}")
        # TODO: Implement activation logic
    
    elif event['type'] == 'invoice.payment_failed':
        # Payment failed - notify user
        logger.warning(f"Stripe payment failed: {event['id']}")
        # TODO: Implement failure handling
    
    elif event['type'] == 'customer.subscription.deleted':
        # Subscription cancelled
        logger.info(f"Stripe subscription cancelled: {event['id']}")
        # TODO: Implement cancellation logic
    
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def flutterwave_webhook(request):
    """
    Flutterwave webhook handler
    
    CRITICAL: Verify webhook signature before processing
    """
    # TODO: Implement Flutterwave webhook verification
    logger.info("Flutterwave webhook received")
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Paystack webhook handler
    
    CRITICAL: Verify webhook signature before processing
    """
    # TODO: Implement Paystack webhook verification
    logger.info("Paystack webhook received")
    return HttpResponse(status=200)
