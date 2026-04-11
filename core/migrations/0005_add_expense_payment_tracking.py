# Generated migration for expense payment tracking

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_add_parent_contact_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='paid_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Bursar/Accountant who processed the payment',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='paid_expenses',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='paid_at',
            field=models.DateTimeField(blank=True, help_text='When payment was processed', null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='payment_reference',
            field=models.CharField(blank=True, help_text='Transaction reference number', max_length=100),
        ),
        migrations.AddField(
            model_name='expense',
            name='bank_account',
            field=models.CharField(blank=True, help_text='Bank account used for payment', max_length=100),
        ),
        migrations.AddField(
            model_name='expense',
            name='is_verified',
            field=models.BooleanField(default=False, help_text='Payment verified by accountant'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='Payment completed'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='requested_by',
            field=models.ForeignKey(
                help_text='Person who requested the expense',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='requested_expenses',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='expense',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Person who approved the expense (Admin/Director)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_expenses',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
