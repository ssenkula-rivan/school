# Generated migration for additional parent contact fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_curriculum_and_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='guardian_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_workplace',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_name',
            field=models.CharField(blank=True, help_text='Second parent/guardian name', max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_relationship',
            field=models.CharField(blank=True, help_text='e.g., Mother, Father', max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_phone',
            field=models.CharField(blank=True, db_index=True, help_text='Second parent phone', max_length=15),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_email',
            field=models.EmailField(blank=True, help_text='Second parent email', max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='parent2_workplace',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='emergency_contact2_name',
            field=models.CharField(blank=True, help_text='Additional emergency contact', max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='emergency_contact2_phone',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='student',
            name='emergency_contact2_relationship',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
