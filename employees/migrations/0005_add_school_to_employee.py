# Generated migration to add school field to Employee

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('employees', '0004_worksubmission_submitted_to_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='school',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='direct_employees',
                to='core.school'
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['school', 'employment_status'], name='emp_school_status_idx'),
        ),
    ]
