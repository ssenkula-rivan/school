# Generated migration for force_password_reset field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_parent_parentstudentlink_parentteachermessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='force_password_reset',
            field=models.BooleanField(default=False, help_text='Force user to reset password on next login'),
        ),
    ]
