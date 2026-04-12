# Generated migration for GatePass and Expense models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_add_parent_contact_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='GatePass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_number', models.CharField(db_index=True, help_text='Unique pass number', max_length=50, unique=True)),
                ('reason', models.CharField(choices=[('medical', 'Medical Emergency'), ('family', 'Family Emergency'), ('appointment', 'Medical Appointment'), ('early_dismissal', 'Early Dismissal'), ('authorized_leave', 'Authorized Leave'), ('parent_request', 'Parent Request'), ('school_activity', 'School Activity'), ('other', 'Other')], max_length=50)),
                ('reason_details', models.TextField(help_text='Detailed reason for leaving')),
                ('exit_date', models.DateField(help_text='Date of exit')),
                ('exit_time', models.TimeField(help_text='Expected exit time')),
                ('expected_return_date', models.DateField(blank=True, help_text='Expected return date', null=True)),
                ('expected_return_time', models.TimeField(blank=True, help_text='Expected return time', null=True)),
                ('actual_exit_time', models.DateTimeField(blank=True, help_text='Actual exit time', null=True)),
                ('actual_return_time', models.DateTimeField(blank=True, help_text='Actual return time', null=True)),
                ('parent_name', models.CharField(help_text='Parent/Guardian name', max_length=200)),
                ('parent_phone', models.CharField(help_text='Parent/Guardian phone', max_length=20)),
                ('parent_id_number', models.CharField(blank=True, help_text='Parent ID/Passport number', max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('used', 'Used'), ('expired', 'Expired')], db_index=True, default='pending', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection')),
                ('notes', models.TextField(blank=True, help_text='Additional notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gate_passes', to='core.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gate_passes', to='core.student')),
                ('requested_by', models.ForeignKey(help_text='Person who requested the pass (teacher, parent, etc.)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_passes', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Head of school or authorized person', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_passes', to=settings.AUTH_USER_MODEL)),
                ('exit_security', models.ForeignKey(blank=True, help_text='Security who processed exit', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exit_passes_processed', to=settings.AUTH_USER_MODEL)),
                ('return_security', models.ForeignKey(blank=True, help_text='Security who processed return', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='return_passes_processed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('expense_type', models.CharField(choices=[('operational', 'Operational Expense'), ('capital', 'Capital Expenditure'), ('salary', 'Salary & Wages'), ('utilities', 'Utilities'), ('maintenance', 'Maintenance & Repairs'), ('supplies', 'Supplies & Materials'), ('transport', 'Transportation'), ('food', 'Food & Catering'), ('events', 'Events & Activities'), ('other', 'Other')], max_length=50)),
                ('category', models.CharField(help_text='Specific category (e.g., Electricity, Stationery)', max_length=100)),
                ('description', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='UGX', max_length=3)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_money', 'Mobile Money'), ('cheque', 'Cheque'), ('card', 'Card Payment')], max_length=20)),
                ('vendor_name', models.CharField(max_length=200)),
                ('vendor_phone', models.CharField(blank=True, max_length=20)),
                ('vendor_email', models.EmailField(blank=True, max_length=254)),
                ('vendor_tin', models.CharField(blank=True, help_text='Tax Identification Number', max_length=50)),
                ('receipt_image', models.ImageField(blank=True, null=True, upload_to='expenses/receipts/')),
                ('invoice_image', models.ImageField(blank=True, null=True, upload_to='expenses/invoices/')),
                ('supporting_documents', models.FileField(blank=True, null=True, upload_to='expenses/documents/')),
                ('expense_date', models.DateField(help_text='Date expense was incurred')),
                ('payment_date', models.DateField(help_text='Date payment was made')),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('paid_at', models.DateTimeField(blank=True, help_text='When payment was processed', null=True)),
                ('payment_reference', models.CharField(blank=True, help_text='Transaction reference number', max_length=100)),
                ('bank_account', models.CharField(blank=True, help_text='Bank account used for payment', max_length=100)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_paid', models.BooleanField(default=False, help_text='Payment completed')),
                ('is_verified', models.BooleanField(default=False, help_text='Payment verified by accountant')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='core.school')),
                ('requested_by', models.ForeignKey(help_text='Person who requested the expense', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_expenses', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Person who approved the expense (Admin/Director)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expenses', to=settings.AUTH_USER_MODEL)),
                ('paid_by', models.ForeignKey(blank=True, help_text='Bursar/Accountant who processed the payment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paid_expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-expense_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='gatepass',
            index=models.Index(fields=['school', 'status'], name='core_gatepa_school__c8e9e5_idx'),
        ),
        migrations.AddIndex(
            model_name='gatepass',
            index=models.Index(fields=['student', '-created_at'], name='core_gatepa_student_0e5b3a_idx'),
        ),
        migrations.AddIndex(
            model_name='gatepass',
            index=models.Index(fields=['pass_number'], name='core_gatepa_pass_nu_f4c8d7_idx'),
        ),
        migrations.AddIndex(
            model_name='gatepass',
            index=models.Index(fields=['exit_date'], name='core_gatepa_exit_da_8a7c2e_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['school', 'expense_date'], name='core_expens_school__9d4e1a_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['expense_type'], name='core_expens_expense_2f5c8b_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['is_approved', 'is_paid'], name='core_expens_is_appr_7a3d9c_idx'),
        ),
    ]
