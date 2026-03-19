from django.db import models
from django.core.cache import cache


class Curriculum(models.Model):
    """International curriculum support for global schools"""
    
    CURRICULUM_TYPES = [
        # National Curricula
        ('american', 'American Curriculum (Common Core)'),
        ('british', 'British Curriculum (National Curriculum)'),
        ('canadian', 'Canadian Curriculum'),
        ('australian', 'Australian Curriculum'),
        ('kenyan', 'Kenyan Curriculum (CBC)'),
        ('ugandan', 'Ugandan Curriculum'),
        ('tanzanian', 'Tanzanian Curriculum'),
        ('nigerian', 'Nigerian Curriculum'),
        ('ghanaian', 'Ghanaian Curriculum'),
        ('south_african', 'South African Curriculum (CAPS)'),
        ('indian', 'Indian Curriculum (CBSE/ICSE)'),
        ('chinese', 'Chinese Curriculum'),
        ('japanese', 'Japanese Curriculum'),
        ('singaporean', 'Singaporean Curriculum'),
        ('malaysian', 'Malaysian Curriculum'),
        ('filipino', 'Filipino Curriculum (K-12)'),
        ('indonesian', 'Indonesian Curriculum'),
        ('thai', 'Thai Curriculum'),
        ('vietnamese', 'Vietnamese Curriculum'),
        ('german', 'German Curriculum'),
        ('french', 'French Curriculum'),
        ('spanish', 'Spanish Curriculum'),
        ('italian', 'Italian Curriculum'),
        ('portuguese', 'Portuguese Curriculum'),
        ('russian', 'Russian Curriculum'),
        ('brazilian', 'Brazilian Curriculum'),
        ('mexican', 'Mexican Curriculum'),
        ('argentine', 'Argentine Curriculum'),
        
        # International Curricula
        ('ib_pyp', 'IB Primary Years Programme'),
        ('ib_myp', 'IB Middle Years Programme'),
        ('ib_dp', 'IB Diploma Programme'),
        ('ib_cp', 'IB Career-related Programme'),
        ('cambridge_primary', 'Cambridge Primary'),
        ('cambridge_lower_secondary', 'Cambridge Lower Secondary'),
        ('cambridge_upper_secondary', 'Cambridge Upper Secondary'),
        ('cambridge_igcse', 'Cambridge IGCSE'),
        ('cambridge_as_a_level', 'Cambridge AS & A Level'),
        ('edexcel', 'Edexcel Curriculum'),
        ('oxford_aqa', 'Oxford AQA Curriculum'),
        
        # Specialized Curricula
        ('montessori', 'Montessori Curriculum'),
        ('waldorf', 'Waldorf Curriculum'),
        ('stem_focused', 'STEM-Focused Curriculum'),
        ('arts_focused', 'Arts-Focused Curriculum'),
        ('language_immersion', 'Language Immersion Curriculum'),
        ('bilingual', 'Bilingual Curriculum'),
        ('special_education', 'Special Education Curriculum'),
        ('gifted_talented', 'Gifted & Talented Curriculum'),
        ('vocational_technical', 'Vocational/Technical Curriculum'),
        ('religious_islamic', 'Islamic Studies Curriculum'),
        ('religious_christian', 'Christian Studies Curriculum'),
        ('religious_hindu', 'Hindu Studies Curriculum'),
        ('religious_buddhist', 'Buddhist Studies Curriculum'),
        
        # Hybrid/Custom
        ('hybrid', 'Hybrid Curriculum'),
        ('custom', 'Custom Curriculum'),
    ]
    
    name = models.CharField(max_length=200)
    curriculum_type = models.CharField(max_length=50, choices=CURRICULUM_TYPES)
    country = models.CharField(max_length=100)
    description = models.TextField()
    grade_levels = models.CharField(max_length=200, help_text="e.g., K-12, Grades 1-6, etc.")
    
    # Assessment Systems
    grading_system = models.CharField(max_length=100, help_text="e.g., A-F, 1-100, GPA, etc.")
    assessment_types = models.TextField(help_text="Types of assessments used")
    
    # Language of Instruction
    primary_language = models.CharField(max_length=50, default='English')
    secondary_languages = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Curriculum'
        verbose_name_plural = 'Curricula'
    
    def __str__(self):
        return f"{self.name} ({self.get_curriculum_type_display()})"
    
    def get_grade_system(self):
        """Return appropriate grade system for this curriculum"""
        grade_systems = {
            'american': {'min': 0, 'max': 100, 'pass': 60, 'format': 'percentage'},
            'british': {'min': 1, 'max': 9, 'pass': 4, 'format': 'grade_1_9'},
            'ib_dp': {'min': 1, 'max': 7, 'pass': 4, 'format': 'ib_grade'},
            'cambridge_igcse': {'min': 'A*', 'max': 'G', 'pass': 'C', 'format': 'igcse_grade'},
            'kenyan': {'min': 1, 'max': 12, 'pass': 5, 'format': 'kcse_grade'},
        }
        return grade_systems.get(self.curriculum_type, grade_systems['american'])


class SchoolCurriculum(models.Model):
    """Link between schools and their curricula"""
    
    school = models.ForeignKey('core.School', on_delete=models.CASCADE)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)
    implementation_year = models.IntegerField()
    
    # Customization
    customizations = models.TextField(blank=True, help_text="Any modifications to the standard curriculum")
    additional_subjects = models.TextField(blank=True, help_text="Additional subjects offered")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'curriculum']
        verbose_name = 'School Curriculum'
        verbose_name_plural = 'School Curricula'
    
    def __str__(self):
        return f"{self.school.name} - {self.curriculum.name}"


class Subject(models.Model):
    """Subjects across different curricula"""
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Curriculum associations
    curricula = models.ManyToManyField(Curriculum, through='CurriculumSubject')
    
    # Subject properties
    is_core = models.BooleanField(default=False)
    is_elective = models.BooleanField(default=False)
    has_practical = models.BooleanField(default=False)
    has_theory = models.BooleanField(default=True)
    
    # Credit/Weight system
    credit_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class CurriculumSubject(models.Model):
    """Link between curricula and subjects"""
    
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Curriculum-specific details
    is_mandatory = models.BooleanField(default=False)
    grade_levels = models.CharField(max_length=200, help_text="Grade levels this subject is taught")
    weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    
    # Assessment weight
    assessment_weight = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    class Meta:
        unique_together = ['curriculum', 'subject']
        verbose_name = 'Curriculum Subject'
        verbose_name_plural = 'Curriculum Subjects'
    
    def __str__(self):
        return f"{self.curriculum.name} - {self.subject.name}"
