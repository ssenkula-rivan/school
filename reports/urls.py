from django.urls import path
from . import views, document_views

app_name = 'reports'

urlpatterns = [
    # Analytics Dashboard
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # PDF Downloads
    path('report-card/<int:report_card_id>/pdf/', views.download_report_card, name='download_report_card'),
    path('receipt/<int:payment_id>/pdf/', views.download_fee_receipt, name='download_fee_receipt'),
    
    # Excel Exports
    path('export/students/', views.export_students, name='export_students'),
    path('export/attendance/', views.export_attendance, name='export_attendance'),
    path('export/financial/', views.export_financial_summary, name='export_financial_summary'),
    
    # Report Dashboards
    path('financial/', views.financial_reports, name='financial_reports'),
    path('attendance/', views.attendance_reports, name='attendance_reports'),
    
    # ========================================================================
    # DOCUMENT GENERATION & PRINTING
    # ========================================================================
    
    # Fees Documents
    path('print/fee-receipt/<int:payment_id>/', document_views.print_fee_receipt, name='print_fee_receipt'),
    path('print/fee-statement/<int:student_id>/', document_views.print_fee_statement, name='print_fee_statement'),
    
    # Academic Documents
    path('print/report-card/<int:report_card_id>/', document_views.print_report_card, name='print_report_card'),
    path('print/student-id-card/<int:student_id>/', document_views.print_student_id_card, name='print_student_id_card'),
    path('print/admission-letter/<int:student_id>/', document_views.print_admission_letter, name='print_admission_letter'),
    path('print/transfer-certificate/<int:student_id>/', document_views.print_transfer_certificate, name='print_transfer_certificate'),
    path('print/attendance-certificate/<int:student_id>/', document_views.print_attendance_certificate, name='print_attendance_certificate'),
    
    # Library Documents
    path('print/library-receipt/<int:borrow_id>/', document_views.print_library_receipt, name='print_library_receipt'),
    path('print/library-card/<int:student_id>/', document_views.print_library_card, name='print_library_card'),
    
    # Inventory Documents
    path('print/purchase-order/<int:purchase_id>/', document_views.print_purchase_order, name='print_purchase_order'),
    path('print/stock-report/', document_views.print_stock_report, name='print_stock_report'),
    path('print/asset-report/', document_views.print_asset_report, name='print_asset_report'),
    
    # Employee Documents
    path('print/payslip/<int:employee_id>/<str:month>/<int:year>/', document_views.print_employee_payslip, name='print_employee_payslip'),
    path('print/employment-letter/<int:employee_id>/', document_views.print_employment_letter, name='print_employment_letter'),
    path('print/leave-approval/<int:leave_id>/', document_views.print_leave_approval, name='print_leave_approval'),
    
    # Bulk Printing
    path('print/bulk-receipts/', document_views.bulk_print_receipts, name='bulk_print_receipts'),
    path('print/bulk-report-cards/', document_views.bulk_print_report_cards, name='bulk_print_report_cards'),
]
