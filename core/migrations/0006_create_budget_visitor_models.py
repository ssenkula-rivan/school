# Generated migration for Budget, BudgetLine, Visitor, and WorkshopExpense models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_create_gatepass_expense_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('budget_type', models.CharField(choices=[('annual', 'Annual Budget'), ('term', 'Term Budget'), ('quarterly', 'Quarterly Budget'), ('monthly', 'Monthly Budget'), ('project', 'Project Budget')], max_length=20)),
                ('title', models.CharField(help_text='e.g., Term 1 Budget 2024, Annual Budget 2024', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_budget', models.DecimalField(decimal_places=2, help_text='Total planned budget', max_digits=15)),
                ('total_spent', models.DecimalField(decimal_places=2, default=0, help_text='Total amount spent', max_digits=15)),
                ('total_committed', models.DecimalField(decimal_places=2, default=0, help_text='Committed but not yet spent', max_digits=15)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted for Approval'), ('approved', 'Approved'), ('active', 'Active'), ('completed', 'Completed'), ('revised', 'Revised')], db_index=True, default='draft', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='core.school')),
                ('academic_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.academicyear')),
                ('prepared_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prepared_budgets', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_budgets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-start_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BudgetLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(help_text='e.g., Salaries, Utilities, Workshops', max_length=100)),
                ('subcategory', models.CharField(blank=True, help_text='e.g., Teacher Salaries, Electricity', max_length=100)),
                ('description', models.TextField()),
                ('allocated_amount', models.DecimalField(decimal_places=2, help_text='Budgeted amount', max_digits=12)),
                ('spent_amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount spent', max_digits=12)),
                ('committed_amount', models.DecimalField(decimal_places=2, default=0, help_text='Committed amount', max_digits=12)),
                ('priority', models.IntegerField(default=3, help_text='1=High, 2=Medium, 3=Low')),
                ('is_essential', models.BooleanField(default=True, help_text='Essential expense')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='core.budget')),
            ],
            options={
                'ordering': ['priority', 'category'],
            },
        ),
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('full_name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('id_number', models.CharField(blank=True, help_text='ID/Passport number', max_length=50)),
                ('company', models.CharField(blank=True, help_text='Company/Organization', max_length=200)),
                ('visitor_type', models.CharField(choices=[('parent', 'Parent/Guardian'), ('vendor', 'Vendor/Supplier'), ('contractor', 'Contractor'), ('inspector', 'Government Inspector'), ('guest_speaker', 'Guest Speaker'), ('workshop_facilitator', 'Workshop Facilitator'), ('maintenance', 'Maintenance Personnel'), ('delivery', 'Delivery Person'), ('official', 'Official Visitor'), ('other', 'Other')], max_length=30)),
                ('purpose', models.CharField(choices=[('meeting', 'Meeting'), ('delivery', 'Delivery'), ('maintenance', 'Maintenance/Repair'), ('workshop', 'Workshop/Training'), ('inspection', 'Inspection'), ('event', 'Event/Program'), ('consultation', 'Consultation'), ('other', 'Other')], max_length=30)),
                ('purpose_details', models.TextField(help_text='Detailed purpose of visit')),
                ('person_to_meet', models.CharField(help_text='Staff member or department', max_length=200)),
                ('visit_date', models.DateField(db_index=True)),
                ('check_in_time', models.DateTimeField(help_text='Actual check-in time')),
                ('expected_checkout_time', models.TimeField(blank=True, null=True)),
                ('check_out_time', models.DateTimeField(blank=True, help_text='Actual check-out time', null=True)),
                ('has_expense', models.BooleanField(default=False, help_text='Visit resulted in expense')),
                ('expense_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('expense_description', models.TextField(blank=True)),
                ('items_brought_in', models.TextField(blank=True, help_text='Items/equipment brought in')),
                ('items_taken_out', models.TextField(blank=True, help_text='Items taken out')),
                ('is_checked_out', models.BooleanField(db_index=True, default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitors', to='core.school')),
                ('checked_in_by', models.ForeignKey(help_text='Security who checked in visitor', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_in_visitors', to=settings.AUTH_USER_MODEL)),
                ('checked_out_by', models.ForeignKey(blank=True, help_text='Security who checked out visitor', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_out_visitors', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-visit_date', '-check_in_time'],
            },
        ),
        migrations.CreateModel(
            name='WorkshopExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workshop_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('target_participants', models.CharField(help_text='e.g., Teachers, Students, Parents', max_length=200)),
                ('expected_attendees', models.IntegerField(help_text='Expected number of attendees')),
                ('actual_attendees', models.IntegerField(blank=True, help_text='Actual number of attendees', null=True)),
                ('facilitator_name', models.CharField(max_length=200)),
                ('facilitator_phone', models.CharField(blank=True, max_length=20)),
                ('facilitator_email', models.EmailField(blank=True, max_length=254)),
                ('facilitator_fee', models.DecimalField(decimal_places=2, help_text='Facilitator payment', max_digits=10)),
                ('venue_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('materials_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('refreshments_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('transport_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('other_costs', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_completed', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshop_expenses', to='core.school')),
                ('budget_line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.budgetline')),
                ('organized_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organized_workshops', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['school', 'status'], name='core_budget_school__4e7a2b_idx'),
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['start_date', 'end_date'], name='core_budget_start_d_8c3f1d_idx'),
        ),
        migrations.AddIndex(
            model_name='visitor',
            index=models.Index(fields=['school', 'visit_date'], name='core_visito_school__9a5e3c_idx'),
        ),
        migrations.AddIndex(
            model_name='visitor',
            index=models.Index(fields=['visitor_type'], name='core_visito_visitor_7d2b4f_idx'),
        ),
        migrations.AddIndex(
            model_name='visitor',
            index=models.Index(fields=['is_checked_out'], name='core_visito_is_chec_6f8a1e_idx'),
        ),
        migrations.AddIndex(
            model_name='workshopexpense',
            index=models.Index(fields=['school', 'start_date'], name='core_worksh_school__3c9d2a_idx'),
        ),
    ]
