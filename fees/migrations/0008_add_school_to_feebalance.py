from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_payment_fields'),
        ('fees', '0007_add_school_to_feepayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='feebalance',
            name='school',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='fee_balances', to='core.school'),
            preserve_default=False,
        ),
    ]
