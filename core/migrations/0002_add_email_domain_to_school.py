# Generated migration to add email_domain to School

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='email_domain',
            field=models.CharField(
                default='school.edu',
                max_length=100,
                unique=True,
                db_index=True,
                help_text="Email domain for school users (e.g., kawandass.edu)"
            ),
            preserve_default=False,
        ),
    ]
