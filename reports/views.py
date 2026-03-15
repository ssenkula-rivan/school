from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from django.utils import timezone

from academics.models import ReportCard, Mark, StudentAttendance
from core.models import Student, AcademicYear
from fees.models import FeePayment
from .utils import (
    export_report_card_pdf, export_fee_receipt_pdf,
    export_students_excel, export_attendance_excel,
    export_financial_summary_excel, generate_academic_analytics_data
)


@login_required
def analytics_dashboard(request):
    """Academic analytics dashboard with charts and statistics"""
    # Get current academic year and term
    current_year = AcademicYear.objects.filter(is_current=True).first()
    term = request.GET.get('term', 'Term 1')
    
    if not current_year:
        return render(request, 'reports/analytics_dashboard.html', {
            'error': 'No active academic year found'
        })
    
    # Generate analytics data
    analytics_data = generate_academic_analytics_data(current_year, term)
    
    context = {
        'academic_year': current_year,
        'term': term,
        'analytics': analytics_data,
        'terms': ['Term 1', 'Term 2', 'Term 3']
    }
    
    return render(request, 'reports/analytics_dashboard.html', context)


@login_required
def download_report_card(request, report_card_id):
    """Download report card as PDF"""
    report_card = get_object_or_404(ReportCard, id=report_card_id)
    return export_report_card_pdf(report_card)


@login_required
def download_fee_receipt(request, payment_id):
    """Download fee receipt as PDF"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    return export_fee_receipt_pdf(payment)


@login_required
def export_students(request):
    """Export students list to Excel"""
    grade = request.GET.get('grade')
    status = request.GET.get('status', 'active')
    
    students = Student.objects.filter(status=status).select_related('grade')
    if grade:
        students = students.filter(grade=grade)
    
    students = students.order_by('admission_number')
    return export_students_excel(students)


@login_required
def export_attendance(request):
    """Export attendance records to Excel"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    grade = request.GET.get('grade')
    
    attendance = StudentAttendance.objects.all()
    
    if start_date:
        attendance = attendance.filter(date__gte=start_date)
    if end_date:
        attendance = attendance.filter(date__lte=end_date)
    if grade:
        attendance = attendance.filter(student__grade=grade)
    
    attendance = attendance.select_related('student', 'marked_by').order_by('-date')
    return export_attendance_excel(attendance)


@login_required
def export_financial_summary(request):
    """Export financial summary to Excel"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        # Default to current month
        today = timezone.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    
    payments = FeePayment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        payment_status='completed'
    ).select_related('student', 'received_by').order_by('payment_date')
    
    return export_financial_summary_excel(payments, start_date, end_date)


@login_required
def financial_reports(request):
    """Financial reports dashboard"""
    # Get date range from request or default to current month
    today = timezone.now()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    
    # Get payments in date range with optimized queries
    payments = FeePayment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).select_related('student', 'student__grade', 'fee_structure', 'fee_structure__academic_year', 'received_by')
    
    # Calculate statistics
    total_collected = payments.filter(payment_status='completed').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    pending_payments = payments.filter(payment_status='pending').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    payment_methods = payments.filter(payment_status='completed').values(
        'payment_method'
    ).annotate(
        total=Sum('amount_paid'),
        count=Count('id')
    )
    
    # Recent payments with pagination
    from django.core.paginator import Paginator
    recent_payments_qs = payments.order_by('-payment_date')
    paginator = Paginator(recent_payments_qs, 20)
    page_number = request.GET.get('page', 1)
    recent_payments = paginator.get_page(page_number)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_collected': total_collected,
        'pending_payments': pending_payments,
        'payment_methods': payment_methods,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'reports/financial_reports.html', context)


@login_required
def attendance_reports(request):
    """Attendance reports dashboard"""
    # Get date range
    today = timezone.now()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    grade = request.GET.get('grade')
    
    # Get attendance records
    attendance = StudentAttendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if grade:
        attendance = attendance.filter(student__grade=grade)
    
    # Calculate statistics
    total_records = attendance.count()
    status_breakdown = attendance.values('status').annotate(
        count=Count('id')
    )
    
    # Calculate attendance rate
    present_count = attendance.filter(status='present').count()
    attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
    
    # Get students with low attendance
    from django.db.models import Case, When, IntegerField
    low_attendance_students = Student.objects.filter(
        status='active'
    ).annotate(
        total_days=Count('studentattendance', filter=Q(
            studentattendance__date__gte=start_date,
            studentattendance__date__lte=end_date
        )),
        present_days=Count('studentattendance', filter=Q(
            studentattendance__date__gte=start_date,
            studentattendance__date__lte=end_date,
            studentattendance__status='present'
        ))
    ).filter(total_days__gt=0)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'grade': grade,
        'total_records': total_records,
        'status_breakdown': status_breakdown,
        'attendance_rate': round(attendance_rate, 2),
        'low_attendance_students': low_attendance_students[:20],
    }
    
    return render(request, 'reports/attendance_reports.html', context)
