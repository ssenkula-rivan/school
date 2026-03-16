# Post-Deployment Checklist

## ✅ Immediate Actions Required

### 1. Change Default Passwords
**CRITICAL SECURITY STEP**

Login to your Render deployment and change these default passwords immediately:

```bash
# Access Render shell and run:
python manage.py shell -c "
from django.contrib.auth.models import User

# Change admin password
admin = User.objects.get(username='admin')
admin.set_password('YOUR_NEW_SECURE_PASSWORD')
admin.save()

# Change accountant password
accountant = User.objects.get(username='accountant')
accountant.set_password('YOUR_NEW_SECURE_PASSWORD')
accountant.save()

print('Passwords updated successfully!')
"
```

### 2. Configure School Settings

1. Login as admin at: `https://your-app.onrender.com/accounts/login/`
2. Go to school configuration
3. Update:
   - School name
   - Contact information
   - Logo (if available)
   - Academic year settings

### 3. Set Up Email (Recommended)

Update environment variables in Render dashboard:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-school-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourschool.com
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the app password in EMAIL_HOST_PASSWORD

### 4. Verify Environment Variables

Check these are set in Render:

- ✅ `DEBUG=False`
- ✅ `ENVIRONMENT=production`
- ✅ `SECRET_KEY=<unique-secret-key>`
- ✅ `DATABASE_URL=<postgresql-url>` (auto-set by Render)
- ✅ `ALLOWED_HOSTS=your-app.onrender.com`
- ✅ `SYSADMIN_PASSWORD=<strong-password>`

### 5. Enable HTTPS (Should be automatic on Render)

Verify:
- Site loads with `https://`
- No SSL warnings
- Redirect from `http://` to `https://` works

### 6. Create Additional Users

Create users for different roles:

**Teachers:**
```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

user = User.objects.create_user('teacher1', 'teacher1@school.com', 'SecurePassword123')
user.is_staff = True
user.first_name = 'John'
user.last_name = 'Teacher'
user.save()

profile = UserProfile.objects.create(
    user=user,
    employee_id='TCH001',
    role='teacher',
    phone='+1234567890'
)
```

**Bursar/Accountant:**
```python
user = User.objects.create_user('bursar', 'bursar@school.com', 'SecurePassword123')
user.is_staff = True
user.first_name = 'Jane'
user.last_name = 'Bursar'
user.save()

profile = UserProfile.objects.create(
    user=user,
    employee_id='BUR001',
    role='bursar',
    phone='+1234567890'
)
```

### 7. Set Up Database Backups

Render provides automatic backups for PostgreSQL, but verify:

1. Go to Render Dashboard → Database
2. Check backup settings
3. Consider additional backup strategy

### 8. Monitor Application

Set up monitoring:

1. **Render Metrics**: Check CPU, Memory, Response times
2. **Error Tracking**: Monitor logs in Render dashboard
3. **Uptime Monitoring**: Consider services like UptimeRobot

### 9. Test Key Features

Test these features work correctly:

- [ ] User login/logout
- [ ] Student registration
- [ ] Fee payment recording
- [ ] Report generation
- [ ] File uploads (student photos, documents)
- [ ] Email notifications (if configured)
- [ ] Password reset functionality

### 10. Security Audit

Run security checks:

```bash
# In Render shell
python manage.py security_audit
```

## 📊 Access URLs

- **Main Site**: https://your-app.onrender.com/
- **Admin Panel**: https://your-app.onrender.com/admin/
- **Login**: https://your-app.onrender.com/accounts/login/

## 🔐 Default Credentials (CHANGE IMMEDIATELY!)

- **Admin**: admin / Admin@123456
- **Accountant**: accountant / Admin@123456

## 📝 Regular Maintenance

### Daily
- Monitor error logs
- Check system performance

### Weekly
- Review user activity
- Check database size
- Verify backups

### Monthly
- Security audit
- Update dependencies
- Review and archive old data

## 🆘 Troubleshooting

### Site Not Loading
1. Check Render deployment status
2. Review deployment logs
3. Verify environment variables
4. Check database connection

### Static Files Not Loading
1. Verify `STATIC_ROOT` setting
2. Run `python manage.py collectstatic`
3. Check Whitenoise configuration

### Database Errors
1. Check DATABASE_URL
2. Verify PostgreSQL is running
3. Check connection limits
4. Review migration status

### Email Not Sending
1. Verify EMAIL_* environment variables
2. Test with: `python manage.py test_email`
3. Check SMTP credentials
4. Review email provider settings

## 📞 Support

For technical issues:
- Check logs in Render dashboard
- Review DEPLOYMENT.md
- Check GitHub issues

## 🎯 Next Steps

1. ✅ Change all default passwords
2. ✅ Configure school settings
3. ✅ Set up email
4. ✅ Create user accounts
5. ✅ Test all features
6. ✅ Train staff on system usage
7. ✅ Import existing student data (if any)
8. ✅ Set up regular backups
9. ✅ Monitor system performance
10. ✅ Plan for scaling as needed

## 🚀 Going Live

Before announcing to users:

- [ ] All default passwords changed
- [ ] School information updated
- [ ] Test accounts created and verified
- [ ] Email notifications working
- [ ] All features tested
- [ ] Staff trained
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Support process defined

---

**Congratulations on your successful deployment! 🎉**

Your School Management System is now live and ready to use.
