from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import json
from datetime import datetime, timedelta


class AcademicAnalytics(models.Model):
    """Advanced academic analytics for schools"""
    
    school = models.ForeignKey('core.School', on_delete=models.CASCADE)
    
    # Time period
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)
    term = models.CharField(max_length=50, blank=True)
    analysis_date = models.DateField()
    
    # Student performance metrics
    total_students = models.IntegerField(default=0)
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    failure_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Grade distribution (JSON)
    grade_distribution = models.JSONField(default=dict)
    
    # Subject performance (JSON)
    subject_performance = models.JSONField(default=dict)
    
    # Attendance metrics
    average_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chronic_absenteeism_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Behavioral metrics
    disciplinary_cases = models.IntegerField(default=0)
    suspension_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Teacher metrics
    student_teacher_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    average_class_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Financial metrics
    fee_collection_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    outstanding_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'academic_year', 'term', 'analysis_date']
        verbose_name = _('Academic Analytics')
        verbose_name_plural = _('Academic Analytics')
    
    def __str__(self):
        return f"{self.school.name} - {self.academic_year.name} Analytics"
    
    def calculate_grade_distribution(self):
        """Calculate grade distribution across all students"""
        from core.models_assessment import AssessmentResult, ReportCard
        
        # Get all assessment results for this period
        results = AssessmentResult.objects.filter(
            student__school=self.school,
            assessment__assessed_date__year=self.analysis_date.year
        )
        
        distribution = {}
        for result in results:
            grade = result.grade
            distribution[grade] = distribution.get(grade, 0) + 1
        
        self.grade_distribution = distribution
        self.save()
        
        return distribution
    
    def calculate_subject_performance(self):
        """Calculate performance by subject"""
        from core.models_assessment import AssessmentResult
        
        results = AssessmentResult.objects.filter(
            student__school=self.school,
            assessment__assessed_date__year=self.analysis_date.year
        ).select_related('assessment__subject')
        
        subject_stats = {}
        for result in results:
            subject = result.assessment.subject
            if subject:
                subject_name = subject.name
                if subject_name not in subject_stats:
                    subject_stats[subject_name] = {
                        'total_students': 0,
                        'total_score': 0,
                        'average_score': 0,
                        'pass_count': 0,
                        'fail_count': 0,
                    }
                
                stats = subject_stats[subject_name]
                stats['total_students'] += 1
                stats['total_score'] += float(result.score)
                
                # Check if passed (assuming 50% is passing)
                if result.percentage >= 50:
                    stats['pass_count'] += 1
                else:
                    stats['fail_count'] += 1
        
        # Calculate averages
        for subject_name, stats in subject_stats.items():
            if stats['total_students'] > 0:
                stats['average_score'] = stats['total_score'] / stats['total_students']
                stats['pass_rate'] = (stats['pass_count'] / stats['total_students']) * 100
        
        self.subject_performance = subject_stats
        self.save()
        
        return subject_stats


class StudentPerformanceTrend(models.Model):
    """Track individual student performance over time"""
    
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE)
    
    # Time period
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)
    term = models.CharField(max_length=50, blank=True)
    assessment_date = models.DateField()
    
    # Performance metrics
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    class_rank = models.IntegerField(null=True, blank=True)
    class_size = models.IntegerField(null=True, blank=True)
    
    # Subject performance (JSON)
    subject_scores = models.JSONField(default=dict)
    
    # Attendance
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Behavior
    disciplinary_incidents = models.IntegerField(default=0)
    
    # Predictions
    predicted_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    at_risk_flag = models.BooleanField(default=False)
    risk_factors = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term', 'assessment_date']
        verbose_name = _('Student Performance Trend')
        verbose_name_plural = _('Student Performance Trends')
    
    def __str__(self):
        return f"{self.student.name} - {self.assessment_date} Performance"
    
    def calculate_risk_factors(self):
        """Identify at-risk students based on multiple factors"""
        risk_factors = []
        
        # Academic risk factors
        if self.gpa and self.gpa < 2.0:
            risk_factors.append('Low GPA')
        
        if self.attendance_rate and self.attendance_rate < 80:
            risk_factors.append('Poor Attendance')
        
        if self.disciplinary_incidents > 3:
            risk_factors.append('Frequent Disciplinary Issues')
        
        # Class rank risk
        if self.class_rank and self.class_size:
            percentile = (self.class_rank / self.class_size) * 100
            if percentile > 80:  # Bottom 20%
                risk_factors.append('Low Class Rank')
        
        # Trend analysis (compare with previous period)
        previous_performance = StudentPerformanceTrend.objects.filter(
            student=self.student,
            assessment_date__lt=self.assessment_date
        ).order_by('-assessment_date').first()
        
        if previous_performance:
            if previous_performance.gpa and self.gpa:
                gpa_change = self.gpa - previous_performance.gpa
                if gpa_change < -0.5:  # Significant drop
                    risk_factors.append('Declining Performance')
        
        self.risk_factors = risk_factors
        self.at_risk_flag = len(risk_factors) >= 2  # At risk if 2+ factors
        self.save()
        
        return risk_factors


class SchoolMetrics(models.Model):
    """Comprehensive school performance metrics"""
    
    school = models.ForeignKey('core.School', on_delete=models.CASCADE)
    
    # Time period
    metric_date = models.DateField()
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)
    
    # Enrollment metrics
    total_enrollment = models.IntegerField(default=0)
    new_enrollments = models.IntegerField(default=0)
    withdrawals = models.IntegerField(default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Academic metrics
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    graduation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    college_acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Staff metrics
    total_teachers = models.IntegerField(default=0)
    student_teacher_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_retention_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Financial metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Facility metrics
    facility_utilization_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    maintenance_cost_per_student = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Technology metrics
        students_with_devices = models.IntegerField(default=0)
    device_penetration_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    internet_bandwidth_per_student = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Parent satisfaction
    parent_satisfaction_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    parent_engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Compliance metrics
    regulatory_compliance_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    safety_incidents = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'metric_date']
        verbose_name = _('School Metrics')
        verbose_name_plural = _('School Metrics')
    
    def __str__(self):
        return f"{self.school.name} - {self.metric_date} Metrics"
    
    def calculate_retention_rate(self):
        """Calculate student retention rate"""
        if self.total_enrollment > 0:
            self.retention_rate = ((self.total_enrollment - self.withdrawals) / self.total_enrollment) * 100
            self.save()
        return self.retention_rate
    
    def calculate_profit_margin(self):
        """Calculate profit margin"""
        if self.total_revenue > 0:
            self.profit_margin = (self.net_profit / self.total_revenue) * 100
            self.save()
        return self.profit_margin


class CustomReport(models.Model):
    """Custom reports for schools"""
    
    REPORT_TYPES = [
        ('academic', 'Academic Report'),
        ('financial', 'Financial Report'),
        ('attendance', 'Attendance Report'),
        ('behavioral', 'Behavioral Report'),
        ('enrollment', 'Enrollment Report'),
        ('staff', 'Staff Report'),
        ('facility', 'Facility Report'),
        ('compliance', 'Compliance Report'),
        ('custom', 'Custom Report'),
    ]
    
    school = models.ForeignKey('core.School', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField()
    
    # Report configuration (JSON)
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    calculations = models.JSONField(default=list)
    
    # Schedule
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semester', 'Semester'),
        ('annually', 'Annually'),
    ], blank=True)
    
    # Distribution
    email_recipients = models.JSONField(default=list)
    auto_email = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Custom Report')
        verbose_name_plural = _('Custom Reports')
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    def generate_report(self):
        """Generate the custom report"""
        # This would contain complex logic to generate reports based on configuration
        # Implementation would depend on specific requirements
        pass


class ReportGeneration(models.Model):
    """Track report generation history"""
    
    custom_report = models.ForeignKey(CustomReport, on_delete=models.CASCADE)
    
    # Generation details
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Results
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    record_count = models.IntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    error_message = models.TextField(blank=True)
    
    # Execution time
    execution_time_seconds = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Report Generation')
        verbose_name_plural = _('Report Generations')
    
    def __str__(self):
        return f"{self.custom_report.name} - {self.generated_at}"
