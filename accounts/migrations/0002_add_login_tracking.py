# Generated migration for login tracking fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_login',
            field=models.DateTimeField(blank=True, help_text='Last login timestamp', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_currently_logged_in',
            field=models.BooleanField(default=False, help_text='Currently logged in'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='login_ip',
            field=models.GenericIPAddressField(blank=True, help_text='Last login IP address', null=True),
        ),
    ]
