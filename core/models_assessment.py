from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class GradingSystem(models.Model):
    """Professional grading systems for different curricula"""
    
    GRADING_TYPES = [
        ('percentage', 'Percentage (0-100)'),
        ('gpa_4_0', 'GPA 4.0 Scale'),
        ('gpa_5_0', 'GPA 5.0 Scale'),
        ('letter_grades', 'Letter Grades (A-F)'),
        ('letter_grades_plus', 'Letter Grades with Plus/Minus (A+, A, A-, etc.)'),
        ('ib_7', 'IB 7-Point Scale'),
        ('igcse', 'IGCSE Grades (A*-G)'),
        ('a_levels', 'A-Level Grades (A*-E)'),
        ('ap_scores', 'AP Scores (1-5)'),
        ('sat_scores', 'SAT Scores (400-1600)'),
        ('act_scores', 'ACT Scores (1-36)'),
        ('kcse', 'KCSE Grades (A-D)'),
        ('csec', 'CSEC Grades (I-VI)'),
        ('baccalaureate', 'French Baccalaureate (0-20)'),
        ('abitur', 'German Abitur (1-15)'),
        ('numeric_1_5', 'Numeric Scale (1-5)'),
        ('numeric_1_10', 'Numeric Scale (1-10)'),
        ('competency_based', 'Competency-Based (Exceeds/Meets/Approaches/Below)'),
        ('mastery_based', 'Mastery-Based (Mastered/Not Mastered)'),
        ('narrative', 'Narrative Assessment'),
        ('portfolio', 'Portfolio Assessment'),
        ('standards_based', 'Standards-Based (1-4)'),
        ('custom', 'Custom Scale'),
    ]
    
    name = models.CharField(max_length=200)
    grading_type = models.CharField(max_length=50, choices=GRADING_TYPES)
    description = models.TextField()
    
    # Scale definition
    min_score = models.DecimalField(max_digits=10, decimal_places=2)
    max_score = models.DecimalField(max_digits=10, decimal_places=2)
    passing_score = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Grade boundaries (JSON field for flexibility)
    grade_boundaries = models.JSONField(default=dict, help_text="JSON object defining grade boundaries")
    
    # Associated curriculum
    curriculum_type = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grading System')
        verbose_name_plural = _('Grading Systems')
    
    def __str__(self):
        return f"{self.name} ({self.get_grading_type_display()})"
    
    def get_grade(self, score):
        """Get grade for a given score"""
        if self.grading_type == 'percentage':
            return self._get_percentage_grade(score)
        elif self.grading_type == 'gpa_4_0':
            return self._get_gpa_grade(score, 4.0)
        elif self.grading_type == 'letter_grades':
            return self._get_letter_grade(score)
        elif self.grading_type == 'ib_7':
            return self._get_ib_grade(score)
        elif self.grading_type == 'igcse':
            return self._get_igcse_grade(score)
        elif self.grading_type == 'kcse':
            return self._get_kcse_grade(score)
        else:
            return str(score)
    
    def _get_percentage_grade(self, score):
        """Standard percentage grading"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 45:
            return 'D+'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _get_gpa_grade(self, score, max_gpa):
        """Convert percentage to GPA"""
        percentage = (score / self.max_score) * 100
        if percentage >= 97:
            return max_gpa
        elif percentage >= 93:
            return max_gpa - 0.3
        elif percentage >= 90:
            return max_gpa - 0.7
        elif percentage >= 87:
            return max_gpa - 1.0
        elif percentage >= 83:
            return max_gpa - 1.3
        elif percentage >= 80:
            return max_gpa - 1.7
        elif percentage >= 77:
            return max_gpa - 2.0
        elif percentage >= 73:
            return max_gpa - 2.3
        elif percentage >= 70:
            return max_gpa - 2.7
        elif percentage >= 67:
            return max_gpa - 3.0
        elif percentage >= 65:
            return max_gpa - 3.3
        elif percentage >= 63:
            return max_gpa - 3.7
        else:
            return max_gpa - 4.0
    
    def _get_letter_grade(self, score):
        """Simple letter grading"""
        percentage = (score / self.max_score) * 100
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def _get_ib_grade(self, score):
        """IB 7-point scale"""
        percentage = (score / self.max_score) * 100
        if percentage >= 90:
            return '7'
        elif percentage >= 80:
            return '6'
        elif percentage >= 70:
            return '5'
        elif percentage >= 60:
            return '4'
        elif percentage >= 50:
            return '3'
        elif percentage >= 40:
            return '2'
        else:
            return '1'
    
    def _get_igcse_grade(self, score):
        """IGCSE grading"""
        percentage = (score / self.max_score) * 100
        if percentage >= 90:
            return 'A*'
        elif percentage >= 85:
            return 'A'
        elif percentage >= 75:
            return 'B'
        elif percentage >= 65:
            return 'C'
        elif percentage >= 55:
            return 'D'
        elif percentage >= 45:
            return 'E'
        elif percentage >= 35:
            return 'F'
        else:
            return 'G'
    
    def _get_kcse_grade(self, score):
        """Kenya KCSE grading"""
        percentage = (score / self.max_score) * 100
        if percentage >= 80:
            return 'A'
        elif percentage >= 75:
            return 'A-'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 65:
            return 'B'
        elif percentage >= 60:
            return 'B-'
        elif percentage >= 55:
            return 'C+'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 45:
            return 'C-'
        elif percentage >= 40:
            return 'D+'
        elif percentage >= 35:
            return 'D'
        elif percentage >= 30:
            return 'D-'
        else:
            return 'E'


class Assessment(models.Model):
    """Professional assessment types"""
    
    ASSESSMENT_TYPES = [
        ('formative', 'Formative Assessment'),
        ('summative', 'Summative Assessment'),
        ('diagnostic', 'Diagnostic Assessment'),
        ('benchmark', 'Benchmark Assessment'),
        ('performance', 'Performance Task'),
        ('portfolio', 'Portfolio Assessment'),
        ('project', 'Project-Based Assessment'),
        ('presentation', 'Presentation'),
        ('practical', 'Practical Assessment'),
        ('oral', 'Oral Assessment'),
        ('written', 'Written Assessment'),
        ('multiple_choice', 'Multiple Choice'),
        ('essay', 'Essay'),
        ('short_answer', 'Short Answer'),
        ('true_false', 'True/False'),
        ('matching', 'Matching'),
        ('fill_blank', 'Fill in the Blank'),
        ('observation', 'Observation'),
        ('interview', 'Interview'),
        ('peer_assessment', 'Peer Assessment'),
        ('self_assessment', 'Self Assessment'),
        ('group_work', 'Group Work Assessment'),
        ('homework', 'Homework'),
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('exam', 'Examination'),
        ('final_exam', 'Final Examination'),
        ('midterm_exam', 'Midterm Examination'),
        ('unit_test', 'Unit Test'),
        ('standardized_test', 'Standardized Test'),
        ('placement_test', 'Placement Test'),
        ('entrance_exam', 'Entrance Examination'),
        ('exit_exam', 'Exit Examination'),
        ('certification_exam', 'Certification Examination'),
        ('licensure_exam', 'Licensure Examination'),
        ('competency_assessment', 'Competency Assessment'),
        ('skills_assessment', 'Skills Assessment'),
        ('aptitude_test', 'Aptitude Test'),
        ('achievement_test', 'Achievement Test'),
        ('proficiency_test', 'Proficiency Test'),
    ]
    
    name = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES)
    description = models.TextField()
    
    # Assessment properties
    max_score = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    
    # Weighting
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    # Curriculum context
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE, null=True, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    
    # Assessment settings
    allow_retake = models.BooleanField(default=False)
    max_attempts = models.IntegerField(default=1)
    time_limit = models.BooleanField(default=True)
    shuffle_questions = models.BooleanField(default=False)
    show_results_immediately = models.BooleanField(default=True)
    
    # Grading
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Assessment')
        verbose_name_plural = _('Assessments')
    
    def __str__(self):
        return f"{self.name} ({self.get_assessment_type_display()})"


class AssessmentResult(models.Model):
    """Student assessment results"""
    
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    
    # Results
    score = models.DecimalField(max_digits=10, decimal_places=2)
    max_score = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=10)
    
    # Additional data
    attempts = models.IntegerField(default=1)
    time_taken_minutes = models.IntegerField(null=True, blank=True)
    
    # Feedback
    feedback = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    
    # Metadata
    assessed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    assessed_date = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'assessment']
        verbose_name = _('Assessment Result')
        verbose_name_plural = _('Assessment Results')
    
    def __str__(self):
        return f"{self.student.name} - {self.assessment.name}: {self.grade}"
    
    def save(self, *args, **kwargs):
        # Calculate percentage and grade
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
        
        # Get grade from grading system
        if self.assessment.grading_system:
            self.grade = self.assessment.grading_system.get_grade(self.score)
        
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    """Professional report cards"""
    
    REPORT_TYPES = [
        ('termly', 'Termly Report'),
        ('semester', 'Semester Report'),
        ('annual', 'Annual Report'),
        ('transcript', 'Academic Transcript'),
        ('progress_report', 'Progress Report'),
        ('behavioral_report', 'Behavioral Report'),
        ('attendance_report', 'Attendance Report'),
        ('skills_report', 'Skills Report'),
        ('portfolio_report', 'Portfolio Report'),
    ]
    
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Period
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)
    term = models.CharField(max_length=50, blank=True)
    
    # Results summary
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    class_rank = models.IntegerField(null=True, blank=True)
    class_size = models.IntegerField(null=True, blank=True)
    
    # Attendance
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    days_late = models.IntegerField(default=0)
    
    # Conduct/Behavior
    conduct_grade = models.CharField(max_length=10, blank=True)
    conduct_comments = models.TextField(blank=True)
    
    # Teacher comments
    class_teacher_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    
    # Metadata
    issued_date = models.DateField()
    signed_by = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'report_type', 'academic_year', 'term']
        verbose_name = _('Report Card')
        verbose_name_plural = _('Report Cards')
    
    def __str__(self):
        return f"{self.student.name} - {self.get_report_type_display()} ({self.academic_year})"
    
    def calculate_gpa(self):
        """Calculate GPA from assessment results"""
        results = AssessmentResult.objects.filter(
            student=self.student,
            assessment__assessed_date__year=self.issued_date.year
        )
        
        if not results:
            return None
        
        total_points = 0
        total_credits = 0
        
        for result in results:
            if result.assessment.grading_system:
                gpa = result.assessment.grading_system._get_gpa_grade(result.score, 4.0)
                total_points += gpa * result.assessment.weight_percentage
                total_credits += result.assessment.weight_percentage
        
        if total_credits > 0:
            return total_points / total_credits
        return None


class ReportCardSubject(models.Model):
    """Individual subject grades on report cards"""
    
    report_card = models.ForeignKey(ReportCard, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE)
    
    # Grades
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=10, blank=True)
    gpa_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Assessment breakdown
    classwork_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    homework_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    test_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exam_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Comments
    teacher_comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['report_card', 'subject']
        verbose_name = _('Report Card Subject')
        verbose_name_plural = _('Report Card Subjects')
    
    def __str__(self):
        return f"{self.report_card.student.name} - {self.subject.name}: {self.grade}"
