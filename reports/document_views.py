"""
Views for document generation and printing
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from core.models import Student
from fees.models import FeePayment
from academics.models import ReportCard
from library.models import BookBorrow
from inventory.models import Purchase
from employees.models import Employee

from .document_generator import (
    generate_fee_receipt,
    generate_student_id_card,
    generate_report_card,
    generate_library_receipt,
    generate_purchase_order,
    generate_employee_payslip,
    generate_admission_letter,
    generate_transfer_certificate,
)


# ============================================================================
# FEES DOCUMENTS
# ============================================================================

@login_required
def print_fee_receipt(request, payment_id):
    """Print fee payment receipt"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    return generate_fee_receipt(payment)


@login_required
def print_fee_statement(request, student_id):
    """Print student fee statement"""
    student = get_object_or_404(Student, id=student_id)
    
    # Get all payments for this student
    payments = FeePayment.objects.filter(
        student=student,
        payment_status='completed'
    ).select_related('fee_structure', 'received_by').order_by('-payment_date')
    
    # Get fee balances
    from fees.models import FeeBalance
    balances = FeeBalance.objects.filter(student=student).select_related('fee_structure')
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'FEE STATEMENT',
        'school_name': config.school_name if config else 'School',
        'student': student,
        'payments': payments,
        'balances': balances,
        'total_paid': sum(p.amount_paid for p in payments),
        'total_balance': sum(b.balance for b in balances),
    }
    
    filename = f'fee_statement_{student.admission_number}.pdf'
    return generate_pdf_document('reports/pdf/fee_statement.html', context, filename)



# ============================================================================
# ACADEMIC DOCUMENTS
# ============================================================================

@login_required
def print_report_card(request, report_card_id):
    """Print student report card"""
    report_card = get_object_or_404(ReportCard, id=report_card_id)
    return generate_report_card(report_card)


@login_required
def print_student_id_card(request, student_id):
    """Print student ID card"""
    student = get_object_or_404(Student, id=student_id)
    return generate_student_id_card(student)


@login_required
def print_admission_letter(request, student_id):
    """Print admission letter"""
    student = get_object_or_404(Student, id=student_id)
    return generate_admission_letter(student)


@login_required
def print_transfer_certificate(request, student_id):
    """Print transfer certificate"""
    student = get_object_or_404(Student, id=student_id)
    return generate_transfer_certificate(student)


@login_required
def print_attendance_certificate(request, student_id):
    """Print attendance certificate"""
    student = get_object_or_404(Student, id=student_id)
    
    from academics.models import StudentAttendance
    from django.db.models import Count, Q
    from datetime import date, timedelta
    
    # Get attendance for current academic year
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    attendance_stats = StudentAttendance.objects.filter(
        student=student,
        date__gte=start_date,
        date__lte=end_date
    ).aggregate(
        total_days=Count('id'),
        present_days=Count('id', filter=Q(status='present')),
        absent_days=Count('id', filter=Q(status='absent')),
    )
    
    attendance_percentage = 0
    if attendance_stats['total_days'] > 0:
        attendance_percentage = (attendance_stats['present_days'] / attendance_stats['total_days']) * 100
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'ATTENDANCE CERTIFICATE',
        'school_name': config.school_name if config else 'School',
        'student': student,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': attendance_stats['total_days'],
        'present_days': attendance_stats['present_days'],
        'absent_days': attendance_stats['absent_days'],
        'attendance_percentage': round(attendance_percentage, 2),
    }
    
    filename = f'attendance_certificate_{student.admission_number}.pdf'
    return generate_pdf_document('reports/pdf/attendance_certificate.html', context, filename)



# ============================================================================
# LIBRARY DOCUMENTS
# ============================================================================

@login_required
def print_library_receipt(request, borrow_id):
    """Print library borrow receipt"""
    borrow = get_object_or_404(BookBorrow, id=borrow_id)
    return generate_library_receipt(borrow)


@login_required
def print_library_card(request, student_id):
    """Print library membership card"""
    student = get_object_or_404(Student, id=student_id)
    
    from library.models import LibraryMember
    membership = get_object_or_404(LibraryMember, student=student)
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'LIBRARY MEMBERSHIP CARD',
        'school_name': config.school_name if config else 'School Library',
        'student': student,
        'membership': membership,
    }
    
    filename = f'library_card_{membership.membership_number}.pdf'
    return generate_pdf_document('reports/pdf/library_card.html', context, filename)


# ============================================================================
# INVENTORY DOCUMENTS
# ============================================================================

@login_required
def print_purchase_order(request, purchase_id):
    """Print purchase order"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return generate_purchase_order(purchase)


@login_required
def print_stock_report(request):
    """Print inventory stock report"""
    from inventory.models import Supply
    
    supplies = Supply.objects.all().select_related('category').order_by('category__name', 'name')
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'INVENTORY STOCK REPORT',
        'school_name': config.school_name if config else 'School',
        'supplies': supplies,
        'generated_date': datetime.now(),
    }
    
    filename = f'stock_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    return generate_pdf_document('reports/pdf/stock_report.html', context, filename)


@login_required
def print_asset_report(request):
    """Print asset report"""
    from inventory.models import Asset
    
    assets = Asset.objects.filter(status='active').select_related('category').order_by('category__name', 'name')
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'ASSET REPORT',
        'school_name': config.school_name if config else 'School',
        'assets': assets,
        'generated_date': datetime.now(),
    }
    
    filename = f'asset_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    return generate_pdf_document('reports/pdf/asset_report.html', context, filename)



# ============================================================================
# EMPLOYEE DOCUMENTS
# ============================================================================

@login_required
def print_employee_payslip(request, employee_id, month, year):
    """Print employee payslip"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Calculate salary details (this should come from a payroll system)
    salary_details = {
        'basic_salary': employee.salary or 0,
        'allowances': 0,
        'deductions': 0,
        'net_salary': employee.salary or 0,
        'payment_date': datetime.now(),
    }
    
    return generate_employee_payslip(employee, month, year, salary_details)


@login_required
def print_employment_letter(request, employee_id):
    """Print employment letter"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'EMPLOYMENT LETTER',
        'school_name': config.school_name if config else 'School',
        'school_address': config.address if config else '',
        'employee': employee,
        'date': datetime.now(),
    }
    
    filename = f'employment_letter_{employee.employee_id}.pdf'
    return generate_pdf_document('reports/pdf/employment_letter.html', context, filename)


@login_required
def print_leave_approval(request, leave_id):
    """Print leave approval letter"""
    from employees.models import LeaveRequest
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'LEAVE APPROVAL LETTER',
        'school_name': config.school_name if config else 'School',
        'leave_request': leave_request,
        'date': datetime.now(),
    }
    
    filename = f'leave_approval_{leave_request.id}.pdf'
    return generate_pdf_document('reports/pdf/leave_approval.html', context, filename)


# ============================================================================
# BULK PRINTING
# ============================================================================

@login_required
def bulk_print_receipts(request):
    """Bulk print receipts for selected payments"""
    payment_ids = request.GET.getlist('payment_ids')
    
    if not payment_ids:
        return HttpResponse("No payments selected", status=400)
    
    payments = FeePayment.objects.filter(id__in=payment_ids)
    
    # Generate combined PDF
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'BULK RECEIPTS',
        'school_name': config.school_name if config else 'School',
        'payments': payments,
    }
    
    filename = f'bulk_receipts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return generate_pdf_document('reports/pdf/bulk_receipts.html', context, filename)


@login_required
def bulk_print_report_cards(request):
    """Bulk print report cards for a class"""
    grade_id = request.GET.get('grade_id')
    term = request.GET.get('term')
    
    if not grade_id or not term:
        return HttpResponse("Grade and term required", status=400)
    
    report_cards = ReportCard.objects.filter(
        student__grade_id=grade_id,
        term=term
    ).select_related('student', 'academic_year')
    
    from .document_generator import generate_pdf_document
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'BULK REPORT CARDS',
        'school_name': config.school_name if config else 'School',
        'report_cards': report_cards,
    }
    
    filename = f'bulk_report_cards_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return generate_pdf_document('reports/pdf/bulk_report_cards.html', context, filename)
