"""
Comprehensive Document Generation System
Generates receipts, invoices, reports, certificates, and other documents
"""

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime
from decimal import Decimal


def generate_pdf_document(template_name, context, filename):
    """
    Generate PDF document from HTML template
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6
        )
        
        # Add content based on context
        if 'title' in context:
            title = Paragraph(context['title'], title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
        
        # Build and return PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except ImportError:
        return HttpResponse("PDF generation library not installed", status=500)



def generate_fee_receipt(payment):
    """Generate fee payment receipt"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'FEE PAYMENT RECEIPT',
        'school_name': config.school_name if config else 'School Management System',
        'school_address': config.address if config else '',
        'school_phone': config.phone if config else '',
        'school_email': config.email if config else '',
        'receipt_number': payment.receipt_number,
        'date': payment.payment_date,
        'student_name': payment.student.get_full_name(),
        'admission_number': payment.student.admission_number,
        'grade': str(payment.student.grade),
        'amount_paid': payment.amount_paid,
        'payment_method': payment.get_payment_method_display(),
        'academic_year': payment.fee_structure.academic_year.name,
        'term': payment.fee_structure.get_term_display(),
        'received_by': payment.received_by.get_full_name() if payment.received_by else 'System',
        'transaction_ref': payment.transaction_reference,
        'remarks': payment.remarks,
    }
    
    filename = f'receipt_{payment.receipt_number}.pdf'
    return generate_pdf_document('reports/pdf/fee_receipt.html', context, filename)


def generate_student_id_card(student):
    """Generate student ID card"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'school_name': config.school_name if config else 'School',
        'student_name': student.get_full_name(),
        'admission_number': student.admission_number,
        'grade': str(student.grade),
        'photo': student.photo.url if student.photo else None,
        'blood_group': student.blood_group,
        'emergency_contact': student.emergency_contact_phone,
    }
    
    filename = f'id_card_{student.admission_number}.pdf'
    return generate_pdf_document('reports/pdf/student_id_card.html', context, filename)



def generate_report_card(report_card):
    """Generate student report card"""
    from academics.models import Mark
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    # Get all marks for this report card
    marks = Mark.objects.filter(
        student=report_card.student,
        exam__academic_year=report_card.academic_year,
        exam__term=report_card.term
    ).select_related('subject', 'exam').order_by('subject__name')
    
    context = {
        'title': 'STUDENT REPORT CARD',
        'school_name': config.school_name if config else 'School',
        'school_address': config.address if config else '',
        'student_name': report_card.student.get_full_name(),
        'admission_number': report_card.student.admission_number,
        'grade': str(report_card.student.grade),
        'academic_year': report_card.academic_year.name,
        'term': report_card.get_term_display(),
        'marks': marks,
        'total_marks': report_card.total_marks,
        'marks_obtained': report_card.marks_obtained,
        'average_percentage': report_card.average_percentage,
        'gpa': report_card.gpa,
        'overall_grade': report_card.overall_grade,
        'class_rank': report_card.class_rank,
        'total_students': report_card.total_students,
        'attendance_percentage': report_card.attendance_percentage,
        'days_present': report_card.days_present,
        'days_absent': report_card.days_absent,
        'teacher_comment': report_card.teacher_comment,
        'headteacher_comment': report_card.headteacher_comment,
        'generated_date': datetime.now(),
    }
    
    filename = f'report_card_{report_card.student.admission_number}_{report_card.term}.pdf'
    return generate_pdf_document('reports/pdf/report_card.html', context, filename)



def generate_library_receipt(borrow):
    """Generate library book borrow receipt"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'LIBRARY BOOK BORROW RECEIPT',
        'school_name': config.school_name if config else 'School Library',
        'receipt_number': f'LIB-{borrow.id:06d}',
        'date': borrow.borrow_date,
        'student_name': borrow.student.get_full_name(),
        'admission_number': borrow.student.admission_number,
        'book_title': borrow.book.title,
        'book_author': borrow.book.author,
        'accession_number': borrow.book.accession_number,
        'borrow_date': borrow.borrow_date,
        'due_date': borrow.due_date,
        'issued_by': borrow.issued_by.get_full_name() if borrow.issued_by else 'Librarian',
        'condition': borrow.condition_on_borrow,
    }
    
    filename = f'library_receipt_{borrow.id}.pdf'
    return generate_pdf_document('reports/pdf/library_receipt.html', context, filename)


def generate_purchase_order(purchase):
    """Generate purchase order document"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    items = purchase.items.select_related('supply').all()
    
    context = {
        'title': 'PURCHASE ORDER',
        'school_name': config.school_name if config else 'School',
        'school_address': config.address if config else '',
        'po_number': purchase.purchase_order_number,
        'date': purchase.purchase_date,
        'supplier': purchase.supplier,
        'supplier_contact': purchase.supplier_contact,
        'items': items,
        'total_amount': purchase.total_amount,
        'tax_amount': purchase.tax_amount,
        'discount_amount': purchase.discount_amount,
        'final_amount': purchase.final_amount,
        'requested_by': purchase.requested_by.get_full_name() if purchase.requested_by else '',
        'notes': purchase.notes,
    }
    
    filename = f'purchase_order_{purchase.purchase_order_number}.pdf'
    return generate_pdf_document('reports/pdf/purchase_order.html', context, filename)



def generate_employee_payslip(employee, month, year, salary_details):
    """Generate employee payslip"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'EMPLOYEE PAYSLIP',
        'school_name': config.school_name if config else 'School',
        'month': month,
        'year': year,
        'employee_name': employee.user.get_full_name(),
        'employee_id': employee.employee_id,
        'department': employee.department.name if employee.department else '',
        'position': employee.position.title if employee.position else '',
        'basic_salary': salary_details.get('basic_salary', 0),
        'allowances': salary_details.get('allowances', 0),
        'deductions': salary_details.get('deductions', 0),
        'net_salary': salary_details.get('net_salary', 0),
        'payment_date': salary_details.get('payment_date'),
    }
    
    filename = f'payslip_{employee.employee_id}_{month}_{year}.pdf'
    return generate_pdf_document('reports/pdf/payslip.html', context, filename)


def generate_admission_letter(student):
    """Generate student admission letter"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'ADMISSION LETTER',
        'school_name': config.school_name if config else 'School',
        'school_address': config.address if config else '',
        'date': datetime.now(),
        'student_name': student.get_full_name(),
        'admission_number': student.admission_number,
        'grade': str(student.grade),
        'admission_date': student.admission_date,
        'guardian_name': student.guardian_name,
    }
    
    filename = f'admission_letter_{student.admission_number}.pdf'
    return generate_pdf_document('reports/pdf/admission_letter.html', context, filename)


def generate_transfer_certificate(student):
    """Generate transfer certificate"""
    from accounts.school_config import SchoolConfiguration
    
    config = SchoolConfiguration.get_config()
    
    context = {
        'title': 'TRANSFER CERTIFICATE',
        'school_name': config.school_name if config else 'School',
        'school_address': config.address if config else '',
        'certificate_number': f'TC-{student.id:06d}',
        'date': datetime.now(),
        'student_name': student.get_full_name(),
        'admission_number': student.admission_number,
        'date_of_birth': student.date_of_birth,
        'admission_date': student.admission_date,
        'last_grade': str(student.grade),
        'conduct': 'Good',
        'reason': 'On request of parent/guardian',
    }
    
    filename = f'transfer_certificate_{student.admission_number}.pdf'
    return generate_pdf_document('reports/pdf/transfer_certificate.html', context, filename)
