# Generated manually to fix critical model issues

from django.db import migrations, models
import django.db.models.deletion
import uuid
import accounts.models


def generate_employee_ids(apps, schema_editor):
    """Generate employee IDs for existing users"""
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for profile in UserProfile.objects.all():
        if not profile.employee_id:
            profile.employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
            profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_userprofile_force_password_reset'),
    ]

    operations = [
        # 1. Fix employee_id field
        migrations.AlterField(
            model_name='userprofile',
            name='employee_id',
            field=models.CharField(default=accounts.models.generate_employee_id, help_text='Auto-generated unique employee ID', max_length=20, unique=True),
        ),
        
        # 2. Increase role field length
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'System Administrator'), ('registrar', 'Registrar'), ('director', 'Director'), ('dos', 'Director of Studies (DOS)'), ('head_of_class', 'Head of Class'), ('deputy_head_teacher', 'Deputy Head Teacher'), ('teacher', 'Teacher'), ('security', 'Security'), ('bursar', 'Bursar'), ('accountant', 'Accountant'), ('hr_manager', 'HR Manager'), ('receptionist', 'Receptionist'), ('librarian', 'Librarian'), ('nurse', 'Nurse'), ('parent', 'Parent'), ('student', 'Student'), ('staff', 'Staff')], default='staff', max_length=50),
        ),
        
        # 3. Add school field to UserProfile (nullable for now)
        migrations.AddField(
            model_name='userprofile',
            name='school',
            field=models.ForeignKey(blank=True, help_text='School this user belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff', to='accounts.schoolconfiguration'),
        ),
        
        # 4. Fix AuditLog object_id field for UUID support
        migrations.AlterField(
            model_name='auditlog',
            name='object_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        
        # 5. Fix LoginLog ip_address field
        migrations.AlterField(
            model_name='loginlog',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        
        # 6. Add GDPR compliance fields
        migrations.AddField(
            model_name='auditlog',
            name='is_anonymised',
            field=models.BooleanField(default=False, help_text='User data anonymised for GDPR compliance'),
        ),
        migrations.AddField(
            model_name='loginlog',
            name='is_anonymised',
            field=models.BooleanField(default=False, help_text='User data anonymised for GDPR compliance'),
        ),
        
        # 7. Add indexes for performance
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['school', 'role'], name='accounts_userprofile_school_role_idx'),
        ),
        migrations.AddIndex(
            model_name='parentstudentlink',
            index=models.Index(fields=['parent'], name='accounts_parentstudentlink_parent_idx'),
        ),
        migrations.AddIndex(
            model_name='parentstudentlink',
            index=models.Index(fields=['student'], name='accounts_parentstudentlink_student_idx'),
        ),
        migrations.AddIndex(
            model_name='parentstudentlink',
            index=models.Index(fields=['is_primary_contact'], name='accounts_parentstudentlink_primary_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['is_anonymised'], name='accounts_auditlog_anonymised_idx'),
        ),
        migrations.AddIndex(
            model_name='loginlog',
            index=models.Index(fields=['is_anonymised'], name='accounts_loginlog_anonymised_idx'),
        ),
        
        # 8. Generate employee IDs for existing users
        migrations.RunPython(generate_employee_ids, migrations.RunPython.noop),
    ]