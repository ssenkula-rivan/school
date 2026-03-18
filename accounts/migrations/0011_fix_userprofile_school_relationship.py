# Generated migration to fix UserProfile school relationship

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_fix_critical_model_issues'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='school',
            field=models.ForeignKey(
                blank=True,
                help_text='School this user belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='staff',
                to='core.school'
            ),
        ),
    ]
