"""
School Configuration Module
Manages school type and level-specific features
"""

from django.db import models
from django.core.cache import cache

class SchoolConfiguration(models.Model):
    """
    Single instance model to store school-wide configuration
    """
    SCHOOL_TYPE_CHOICES = [
        # Early Childhood Education
        ('daycare', 'Daycare/Childcare Center'),
        ('preschool', 'Preschool/Pre-K'),
        ('kindergarten', 'Kindergarten'),
        
        # Primary Education
        ('primary', 'Primary School (Grades 1-6)'),
        ('elementary', 'Elementary School (K-5)'),
        ('junior_primary', 'Junior Primary School'),
        
        # Secondary Education  
        ('middle_school', 'Middle School (Grades 6-8)'),
        ('junior_high', 'Junior High School (Grades 7-9)'),
        ('high_school', 'High School (Grades 9-12)'),
        ('senior_high', 'Senior High School (Grades 11-12)'),
        ('secondary', 'Secondary School (O-Level & A-Level)'),
        
        # Higher Education
        ('college', 'College'),
        ('university', 'University'),
        ('technical_college', 'Technical College'),
        ('vocational_college', 'Vocational College'),
        ('community_college', 'Community College'),
        ('polytechnic', 'Polytechnic Institute'),
        
        # Specialized Education
        ('special_education', 'Special Education School'),
        ('stem_school', 'STEM School'),
        ('arts_school', 'Arts School'),
        ('music_school', 'Music Conservatory'),
        ('sports_academy', 'Sports Academy'),
        ('language_school', 'Language School'),
        ('international_school', 'International School'),
        ('montessori', 'Montessori School'),
        ('waldorf', 'Waldorf School'),
        
        # Religious/Parochial
        ('catholic_school', 'Catholic School'),
        ('christian_school', 'Christian School'),
        ('islamic_school', 'Islamic School'),
        ('jewish_school', 'Jewish School'),
        ('buddhist_school', 'Buddhist School'),
        ('hindu_school', 'Hindu School'),
        
        # Alternative Education
        ('charter_school', 'Charter School'),
        ('magnet_school', 'Magnet School'),
        ('homeschool_coop', 'Homeschool Cooperative'),
        ('online_school', 'Online/Virtual School'),
        ('microschool', 'Microschool'),
        
        # Adult/Continuing Education
        ('adult_education', 'Adult Education Center'),
        ('continuing_ed', 'Continuing Education'),
        ('corporate_training', 'Corporate Training Center'),
        ('professional_development', 'Professional Development Institute'),
        
        # Special Purpose
        ('military_academy', 'Military Academy'),
        ('boarding_school', 'Boarding School'),
        ('hospital_school', 'Hospital School'),
        ('prison_education', 'Correctional Education'),
        ('refugee_school', 'Refugee Education Center'),
        
        # Legacy/Combined
        ('nursery', 'Nursery School'),
        ('combined', 'Combined School (Multiple Levels)'),
    ]
    
    INSTITUTION_TYPE_CHOICES = [
        ('government', 'Government Institution'),
        ('private', 'Private Institution'),
        ('religious', 'Religious Institution'),
        ('international', 'International Institution'),
        ('vocational', 'Vocational/Technical Institution'),
        ('special_needs', 'Special Needs Institution'),
        ('boarding', 'Boarding Institution'),
        ('day', 'Day Institution'),
        ('mixed', 'Mixed (Day & Boarding)'),
    ]
    
    # Basic School Information
    school_name = models.CharField(max_length=200)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPE_CHOICES, default='private')
    school_motto = models.CharField(max_length=200, blank=True)
    school_logo = models.ImageField(upload_to='school/', blank=True, null=True)
    
    # Contact Information
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Academic Configuration
    current_academic_year = models.ForeignKey(
        'core.AcademicYear', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='current_for_school'
    )
    
    # Feature Flags (automatically set based on school type)
    enable_subjects = models.BooleanField(default=True)
    enable_exams = models.BooleanField(default=True)
    enable_report_cards = models.BooleanField(default=True)
    enable_library = models.BooleanField(default=False)
    enable_transport = models.BooleanField(default=False)
    enable_hostel = models.BooleanField(default=False)
    enable_parent_portal = models.BooleanField(default=True)
    enable_online_classes = models.BooleanField(default=False)
    enable_research = models.BooleanField(default=False)
    enable_departments = models.BooleanField(default=False)
    enable_courses = models.BooleanField(default=False)
    enable_semesters = models.BooleanField(default=False)
    
    # System Settings
    is_configured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'School Configuration'
        verbose_name_plural = 'School Configuration'
    
    def __str__(self):
        return f"{self.school_name} - {self.get_school_type_display()}"
    
    def save(self, *args, **kwargs):
        # Remove single configuration restriction - allow multiple schools
        # Auto-configure features based on school type
        self._configure_features()
        
        super().save(*args, **kwargs)
        
        # Clear cache when configuration changes
        cache.delete('school_config')
    
    def _configure_features(self):
        """Auto-configure features based on school type"""
        if self.school_type == 'nursery':
            self.enable_subjects = False
            self.enable_exams = False
            self.enable_report_cards = True  # Simple progress reports
            self.enable_library = False
            self.enable_transport = True
            self.enable_hostel = False
            self.enable_parent_portal = True
            self.enable_online_classes = False
            self.enable_research = False
            self.enable_departments = False
            self.enable_courses = False
            self.enable_semesters = False
            
        elif self.school_type == 'primary':
            self.enable_subjects = True
            self.enable_exams = True
            self.enable_report_cards = True
            self.enable_library = True
            self.enable_transport = True
            self.enable_hostel = False
            self.enable_parent_portal = True
            self.enable_online_classes = False
            self.enable_research = False
            self.enable_departments = False
            self.enable_courses = False
            self.enable_semesters = False
            
        elif self.school_type == 'secondary':
            self.enable_subjects = True
            self.enable_exams = True
            self.enable_report_cards = True
            self.enable_library = True
            self.enable_transport = True
            self.enable_hostel = True
            self.enable_parent_portal = True
            self.enable_online_classes = True
            self.enable_research = False
            self.enable_departments = False
            self.enable_courses = False
            self.enable_semesters = False
            
        elif self.school_type == 'college':
            self.enable_subjects = True
            self.enable_exams = True
            self.enable_report_cards = True
            self.enable_library = True
            self.enable_transport = False
            self.enable_hostel = True
            self.enable_parent_portal = False
            self.enable_online_classes = True
            self.enable_research = True
            self.enable_departments = True
            self.enable_courses = True
            self.enable_semesters = True
            
        elif self.school_type == 'university':
            self.enable_subjects = False  # Universities use courses
            self.enable_exams = True
            self.enable_report_cards = False  # Universities use transcripts
            self.enable_library = True
            self.enable_transport = False
            self.enable_hostel = True
            self.enable_parent_portal = False
            self.enable_online_classes = True
            self.enable_research = True
            self.enable_departments = True
            self.enable_courses = True
            self.enable_semesters = True
            
        elif self.school_type == 'combined':
            # Enable all features for combined schools
            self.enable_subjects = True
            self.enable_exams = True
            self.enable_report_cards = True
            self.enable_library = True
            self.enable_transport = True
            self.enable_hostel = True
            self.enable_parent_portal = True
            self.enable_online_classes = True
            self.enable_research = False
            self.enable_departments = False
            self.enable_courses = False
            self.enable_semesters = False
    
    @classmethod
    def get_config(cls):
        """Get the school configuration (cached)"""
        config = cache.get('school_config')
        if config is None:
            config = cls.objects.first()
            if config:
                cache.set('school_config', config, 3600)  # Cache for 1 hour
        return config
    
    @classmethod
    def is_school_configured(cls):
        """Check if school has been configured"""
        config = cls.get_config()
        return config and config.is_configured
    
    def get_grade_terminology(self):
        """Get the appropriate grade terminology for this school type"""
        terminology = {
            'nursery': {
                'grade': 'Class',
                'student': 'Child',
                'teacher': 'Caregiver',
                'exam': 'Assessment',
            },
            'primary': {
                'grade': 'Grade',
                'student': 'Student',
                'teacher': 'Teacher',
                'exam': 'Exam',
            },
            'secondary': {
                'grade': 'Form/Senior',
                'student': 'Student',
                'teacher': 'Teacher',
                'exam': 'Exam',
            },
            'college': {
                'grade': 'Year',
                'student': 'Student',
                'teacher': 'Lecturer',
                'exam': 'Exam',
            },
            'university': {
                'grade': 'Year',
                'student': 'Student',
                'teacher': 'Professor/Lecturer',
                'exam': 'Exam',
            },
            'combined': {
                'grade': 'Level',
                'student': 'Student',
                'teacher': 'Teacher',
                'exam': 'Exam',
            },
        }
        return terminology.get(self.school_type, terminology['primary'])


def get_school_config():
    """Helper function to get school configuration"""
    return SchoolConfiguration.get_config()


def is_feature_enabled(feature_name):
    """Check if a specific feature is enabled"""
    config = get_school_config()
    if not config:
        return False
    return getattr(config, f'enable_{feature_name}', False)
