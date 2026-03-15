# Generated migration to add school field to FeePayment

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('fees', '0006_alter_feebalance_due_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feepayment',
            name='school',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='payments',
                to='core.school'
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='feepayment',
            index=models.Index(fields=['school', 'student', 'fee_structure'], name='payment_lookup'),
        ),
        migrations.AddIndex(
            model_name='feepayment',
            index=models.Index(fields=['school', 'payment_status'], name='payment_status_idx'),
        ),
        migrations.AddIndex(
            model_name='feepayment',
            index=models.Index(fields=['school', '-payment_date'], name='payment_date_idx'),
        ),
        migrations.AddIndex(
            model_name='feepayment',
            index=models.Index(fields=['school', 'receipt_number'], name='payment_receipt_idx'),
        ),
        migrations.AddConstraint(
            model_name='feepayment',
            constraint=models.UniqueConstraint(
                fields=['school', 'receipt_number'],
                name='unique_receipt_per_school'
            ),
        ),
    ]
