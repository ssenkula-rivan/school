# accounting/forms.py
from django import forms
from .models import Transaction, JournalEntry, Invoice, Receipt

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['account', 'amount', 'entry_type']
        widgets = {
            'account': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'entry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
        labels = {
            'account': 'Account',
            'amount': 'Amount ($)',
            'entry_type': 'Entry Type'
        }

JournalEntryFormSet = forms.inlineformset_factory(
    Transaction, JournalEntry, form=JournalEntryForm, extra=2, can_delete=True
)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'reference_number']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter transaction description',
                'required': True
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number (optional)'
            })
        }
        labels = {
            'date': 'Transaction Date',
            'description': 'Description',
            'reference_number': 'Reference Number'
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'amount', 'due_date', 'status', 'scanned_copy']
        widgets = {
            'client': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Client name',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'scanned_copy': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            })
        }
        labels = {
            'client': 'Client Name',
            'amount': 'Invoice Amount ($)',
            'due_date': 'Due Date',
            'status': 'Payment Status',
            'scanned_copy': 'Attach Document'
        }

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['receipt_type', 'vendor', 'amount', 'date', 'category', 'description', 'receipt_image', 
                  'student_name', 'grade_class', 'school_year']
        widgets = {
            'receipt_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'vendor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vendor/Merchant/School name',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes or details',
                'rows': 3
            }),
            'receipt_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Student name (optional for school expenses)'
            }),
            'grade_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Grade 5, Class 3A'
            }),
            'school_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024-2025'
            })
        }
        labels = {
            'receipt_type': 'Receipt Type',
            'vendor': 'Vendor/Merchant/School',
            'amount': 'Amount ($)',
            'date': 'Receipt Date',
            'category': 'Category',
            'description': 'Description',
            'receipt_image': 'Upload Receipt Image',
            'student_name': 'Student Name',
            'grade_class': 'Grade/Class',
            'school_year': 'School Year'
        }
