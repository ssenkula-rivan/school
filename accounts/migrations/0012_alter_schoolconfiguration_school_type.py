# Generated migration for SchoolConfiguration school_type field length increase

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_fix_userprofile_school_relationship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolconfiguration',
            name='school_type',
            field=models.CharField(max_length=50),
        ),
    ]
