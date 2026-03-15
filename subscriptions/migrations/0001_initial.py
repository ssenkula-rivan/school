# Generated migration for subscriptions app

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('yearly', 'Yearly'), ('lifetime', 'Lifetime')], default='monthly', max_length=20)),
                ('max_students', models.IntegerField(default=100, help_text='Maximum number of active students', validators=[django.core.validators.MinValueValidator(1)])),
                ('max_teachers', models.IntegerField(default=10, help_text='Maximum number of teachers', validators=[django.core.validators.MinValueValidator(1)])),
                ('max_staff', models.IntegerField(default=20, help_text='Maximum number of total staff', validators=[django.core.validators.MinValueValidator(1)])),
                ('max_storage_gb', models.IntegerField(default=5, help_text='Maximum storage in GB', validators=[django.core.validators.MinValueValidator(1)])),
                ('feature_flags', models.JSONField(default=dict, help_text='Feature flags: {"advanced_reports": true, "sms_integration": false, ...}')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('is_public', models.BooleanField(default=True, help_text='Show on pricing page')),
                ('sort_order', models.IntegerField(default=0)),
                ('trial_days', models.IntegerField(default=14, help_text='Number of trial days (0 = no trial)', validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['sort_order', 'price'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('trial', 'Trial'), ('active', 'Active'), ('suspended', 'Suspended'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], db_index=True, default='trial', max_length=20)),
                ('current_period_start', models.DateField(db_index=True)),
                ('current_period_end', models.DateField(db_index=True)),
                ('trial_start', models.DateField(blank=True, null=True)),
                ('trial_end', models.DateField(blank=True, db_index=True, null=True)),
                ('external_payment_id', models.CharField(blank=True, db_index=True, help_text='Stripe/Flutterwave/Paystack subscription ID', max_length=255)),
                ('external_customer_id', models.CharField(blank=True, help_text='External customer ID', max_length=255)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('cancel_reason', models.TextField(blank=True)),
                ('cancel_at_period_end', models.BooleanField(default=False, help_text='Cancel when current period ends')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='subscriptions.plan')),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='core.school')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SubscriptionInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')], db_index=True, default='pending', max_length=20)),
                ('issue_date', models.DateField(db_index=True)),
                ('due_date', models.DateField(db_index=True)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('external_invoice_id', models.CharField(blank=True, max_length=255)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='subscriptions.subscription')),
            ],
            options={
                'ordering': ['-issue_date'],
            },
        ),
        migrations.AddIndex(
            model_name='plan',
            index=models.Index(fields=['is_active', 'is_public'], name='subscriptio_is_acti_e8c8e5_idx'),
        ),
        migrations.AddIndex(
            model_name='subscriptioninvoice',
            index=models.Index(fields=['subscription', 'status'], name='subscriptio_subscri_8f9a3c_idx'),
        ),
        migrations.AddIndex(
            model_name='subscriptioninvoice',
            index=models.Index(fields=['-issue_date'], name='subscriptio_issue_d_4e7b2a_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['status', 'current_period_end'], name='subscriptio_status_9c4d1e_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['trial_end'], name='subscriptio_trial_e_7a2f8b_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['external_payment_id'], name='subscriptio_externa_6b3e9d_idx'),
        ),
    ]
