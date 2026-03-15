from django.contrib import admin
from academics.models import ReportCard, Mark, StudentAttendance
from fees.models import FeePayment


@admin.action(description='Export selected report cards as PDF')
def export_report_cards_pdf(modeladmin, request, queryset):
    """Export multiple report cards as PDFs"""
    from django.http import HttpResponse
    from .utils import export_report_card_pdf
    
    if queryset.count() == 1:
        return export_report_card_pdf(queryset.first())
    else:
        modeladmin.message_user(request, "Please select only one report card at a time for PDF export")


@admin.action(description='Export selected payments as receipts')
def export_payment_receipts(modeladmin, request, queryset):
    """Export payment receipts as PDFs"""
    from django.http import HttpResponse
    from .utils import export_fee_receipt_pdf
    
    if queryset.count() == 1:
        return export_fee_receipt_pdf(queryset.first())
    else:
        modeladmin.message_user(request, "Please select only one payment at a time for PDF export")


# Add custom actions to existing admin classes
def register_report_actions():
    """Register report export actions to existing admin classes"""
    try:
        from academics.admin import ReportCardAdmin
        if export_report_cards_pdf not in ReportCardAdmin.actions:
            ReportCardAdmin.actions = list(ReportCardAdmin.actions or []) + [export_report_cards_pdf]
    except:
        pass
    
    try:
        from fees.admin import FeePaymentAdmin
        if export_payment_receipts not in FeePaymentAdmin.actions:
            FeePaymentAdmin.actions = list(FeePaymentAdmin.actions or []) + [export_payment_receipts]
    except:
        pass


# Register actions when admin is ready
register_report_actions()

