# Generated migration for payment tracking fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='school',
            name='last_payment_date',
            field=models.DateField(blank=True, help_text='Date of last payment', null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='next_payment_due_date',
            field=models.DateField(blank=True, help_text='Next payment due date', null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='is_access_blocked',
            field=models.BooleanField(default=False, help_text='Block access for unpaid schools'),
        ),
        migrations.AddField(
            model_name='school',
            name='payment_notes',
            field=models.TextField(blank=True, help_text='Notes about payment status'),
        ),
    ]
