from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Sum, Count
from core.models import Student, Grade, AcademicYear
from decimal import Decimal


class Subject(models.Model):
    """
    Academic subjects - supports all school levels
    
    TENANT ISOLATION: Global subjects (no school FK)
    Shared across all schools - not tenant-specific
    """
    SUBJECT_CATEGORY_CHOICES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective Subject'),
        ('compulsory', 'Compulsory Subject'),
        ('optional', 'Optional Subject'),
    ]
    
    LEVEL_CHOICES = [
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('college', 'College'),
        ('university', 'University'),
        ('all', 'All Levels'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=SUBJECT_CATEGORY_CHOICES, default='core')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all')
    credit_hours = models.IntegerField(default=3, help_text="For college/university")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSubject(models.Model):
    """
    Subject allocation to classes with teachers
    
    TENANT ISOLATION: Indirect via Grade and AcademicYear (both have school FK)
    Automatically filtered when querying through relationships
    """
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_allocations')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_subjects')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='class_subjects')
    
    # Timetable fields
    periods_per_week = models.IntegerField(default=5)
    
    class Meta:
        unique_together = ['grade', 'subject', 'academic_year']
        ordering = ['grade', 'subject']
    
    def __str__(self):
        return f"{self.grade} - {self.subject} ({self.teacher.get_full_name() if self.teacher else 'No Teacher'})"


class Timetable(models.Model):
    """Class timetable/schedule"""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='timetable_slots')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['class_subject', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.class_subject.grade} - {self.class_subject.subject} - {self.day_of_week} {self.start_time}"


class Exam(models.Model):
    """
    Examination/Assessment - supports all school levels
    
    TENANT ISOLATION: Indirect via AcademicYear and Grade (both have school FK)
    Automatically filtered when querying through relationships
    """
    EXAM_TYPE_CHOICES = [
        # Primary/Secondary
        ('cat', 'Continuous Assessment Test'),
        ('midterm', 'Mid-Term Exam'),
        ('final', 'Final Exam'),
        ('mock', 'Mock Exam'),
        ('bot', 'Beginning of Term'),
        ('eot', 'End of Term'),
        # College/University
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('practical', 'Practical Exam'),
        ('coursework', 'Coursework'),
        ('thesis', 'Thesis/Dissertation'),
    ]
    
    TERM_CHOICES = [
        ('1', 'Term 1 / Semester 1'),
        ('2', 'Term 2 / Semester 2'),
        ('3', 'Term 3'),
    ]
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    max_marks = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    pass_marks = models.IntegerField(default=40, validators=[MinValueValidator(1)])
    weightage = models.DecimalField(max_digits=5, decimal_places=2, default=100, help_text="Percentage weightage in final grade")
    
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=False, help_text="Results published to students")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['grade', 'subject']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} - Term {self.term}"


class GradeScale(models.Model):
    """Grading scale configuration - different for each school level"""
    LEVEL_CHOICES = Subject.LEVEL_CHOICES
    
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.level})"


class GradeScaleRange(models.Model):
    """Grade scale ranges"""
    grade_scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE, related_name='ranges')
    grade = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, help_text="GPA point")
    description = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-min_percentage']
        unique_together = ['grade_scale', 'grade']
    
    def __str__(self):
        return f"{self.grade} ({self.min_percentage}-{self.max_percentage}%)"


class Mark(models.Model):
    """
    Student marks/grades
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    
    CRITICAL SECURITY:
    - Uses PROTECT on ForeignKeys to prevent accidental deletion
    - Validates marks are non-negative
    - Audit trail via entered_by field
    """
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='marks')
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name='marks')
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    is_absent = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entered_marks')
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'exam']
        ordering = ['student', 'subject']
        indexes = [
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['exam', 'subject']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(marks_obtained__gte=0),
                name='marks_non_negative'
            )
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.code} - {self.marks_obtained}/{self.exam.max_marks}"
    
    def calculate_grade(self):
        """Calculate grade based on percentage and grade scale"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self.is_absent:
            self.grade = 'ABS'
            self.grade_point = 0
            return
        
        if self.exam.max_marks == 0:
            logger.warning(f'Exam {self.exam.id} has max_marks=0')
            self.percentage = 0
            self.grade = 'N/A'
            self.grade_point = 0
            return
        
        self.percentage = (self.marks_obtained / self.exam.max_marks) * 100
        
        # Get grade scale for student's level
        try:
            from accounts.school_config import SchoolConfiguration
            config = SchoolConfiguration.get_config()
            
            if config:
                grade_scale = GradeScale.objects.filter(
                    level=config.school_type,
                    is_default=True
                ).first()
                
                if grade_scale:
                    grade_range = grade_scale.ranges.filter(
                        min_percentage__lte=self.percentage,
                        max_percentage__gte=self.percentage
                    ).first()
                    
                    if grade_range:
                        self.grade = grade_range.grade
                        self.grade_point = grade_range.grade_point
                        return
        except Exception as e:
            logger.error(f'Error calculating grade for mark {self.id}: {e}')
        
        # Default grading if no scale found
        if self.percentage >= 80:
            self.grade = 'A'
            self.grade_point = Decimal('4.0')
        elif self.percentage >= 70:
            self.grade = 'B'
            self.grade_point = Decimal('3.0')
        elif self.percentage >= 60:
            self.grade = 'C'
            self.grade_point = Decimal('2.0')
        elif self.percentage >= 50:
            self.grade = 'D'
            self.grade_point = Decimal('1.0')
        elif self.percentage >= 40:
            self.grade = 'E'
            self.grade_point = Decimal('0.5')
        else:
            self.grade = 'F'
            self.grade_point = Decimal('0.0')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate marks not exceed max marks
        if self.marks_obtained > self.exam.max_marks:
            raise ValidationError(f'Marks obtained ({self.marks_obtained}) cannot exceed maximum marks ({self.exam.max_marks})')
        
        # Validate marks are non-negative
        if self.marks_obtained < 0:
            raise ValidationError('Marks cannot be negative')
        
        # Validate exam max marks
        if self.exam.max_marks <= 0:
            raise ValidationError('Exam maximum marks must be greater than zero')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        self.calculate_grade()
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    """
    Student report cards
    
    TENANT ISOLATION: Indirect via Student and AcademicYear (both have school FK)
    Automatically filtered when querying through relationships
    """
    TERM_CHOICES = Exam.TERM_CHOICES
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='report_cards')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='report_cards')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Grade Point Average")
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Cumulative GPA")
    overall_grade = models.CharField(max_length=5, blank=True)
    
    class_rank = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(default=0)
    
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    
    teacher_comment = models.TextField(blank=True)
    headteacher_comment = models.TextField(blank=True)
    
    promoted_to_next_class = models.BooleanField(default=False)
    next_grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name='promoted_students')
    
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['academic_year', 'term']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.academic_year} - Term {self.term}"
    
    def calculate_results(self):
        """Calculate all report card metrics"""
        # Get all marks for this student in this term
        marks = Mark.objects.filter(
            student=self.student,
            exam__academic_year=self.academic_year,
            exam__term=self.term
        ).select_related('exam', 'subject')
        
        if not marks.exists():
            return
        
        # Calculate totals
        self.total_marks = sum(mark.exam.max_marks for mark in marks)
        self.marks_obtained = sum(mark.marks_obtained for mark in marks if not mark.is_absent)
        
        # Calculate percentage
        if self.total_marks > 0:
            self.average_percentage = (self.marks_obtained / self.total_marks) * 100
        
        # Calculate GPA
        total_grade_points = sum(mark.grade_point for mark in marks if not mark.is_absent)
        subject_count = marks.filter(is_absent=False).count()
        if subject_count > 0:
            self.gpa = total_grade_points / subject_count
        
        # Calculate overall grade
        if self.average_percentage >= 80:
            self.overall_grade = 'A'
        elif self.average_percentage >= 70:
            self.overall_grade = 'B'
        elif self.average_percentage >= 60:
            self.overall_grade = 'C'
        elif self.average_percentage >= 50:
            self.overall_grade = 'D'
        elif self.average_percentage >= 40:
            self.overall_grade = 'E'
        else:
            self.overall_grade = 'F'
        
        # Calculate class rank
        self.calculate_rank()
        
        self.save()
    
    def calculate_rank(self):
        """Calculate student's rank in class"""
        # Get all report cards for same grade, year, and term
        same_class_reports = ReportCard.objects.filter(
            student__grade=self.student.grade,
            academic_year=self.academic_year,
            term=self.term
        ).order_by('-average_percentage')
        
        self.total_students = same_class_reports.count()
        
        # Find rank
        for index, report in enumerate(same_class_reports, start=1):
            if report.id == self.id:
                self.class_rank = index
                break


class StudentAttendance(models.Model):
    """
    Daily student attendance
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
        ('sick', 'Sick'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', db_index=True)
    remarks = models.TextField(blank=True)
    
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class StudentPromotion(models.Model):
    """
    Student promotion/progression records
    
    TENANT ISOLATION: Indirect via Student, Grade, and AcademicYear (all have school FK)
    Automatically filtered when querying through relationships
    """
    STATUS_CHOICES = [
        ('promoted', 'Promoted'),
        ('retained', 'Retained'),
        ('transferred', 'Transferred'),
        ('graduated', 'Graduated'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='promotions')
    from_grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='promoted_from')
    to_grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='promoted_to', null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='promotions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True)
    
    promoted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='student_promotions')
    promoted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-promoted_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.status} - {self.academic_year}"
