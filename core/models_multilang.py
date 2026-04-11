from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    """Supported languages for international schools"""
    
    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('zh', 'Chinese (Mandarin)'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ar', 'Arabic'),
        ('hi', 'Hindi'),
        ('sw', 'Swahili'),
        ('af', 'Afrikaans'),
        ('zu', 'Zulu'),
        ('xh', 'Xhosa'),
        ('ha', 'Hausa'),
        ('ig', 'Igbo'),
        ('yo', 'Yoruba'),
        ('th', 'Thai'),
        ('vi', 'Vietnamese'),
        ('id', 'Indonesian'),
        ('ms', 'Malay'),
        ('tl', 'Filipino'),
        ('bn', 'Bengali'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('mr', 'Marathi'),
        ('gu', 'Gujarati'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('pa', 'Punjabi'),
        ('ur', 'Urdu'),
        ('fa', 'Persian'),
        ('tr', 'Turkish'),
        ('pl', 'Polish'),
        ('nl', 'Dutch'),
        ('sv', 'Swedish'),
        ('da', 'Danish'),
        ('no', 'Norwegian'),
        ('fi', 'Finnish'),
        ('el', 'Greek'),
        ('he', 'Hebrew'),
        ('cs', 'Czech'),
        ('hu', 'Hungarian'),
        ('ro', 'Romanian'),
        ('bg', 'Bulgarian'),
        ('hr', 'Croatian'),
        ('sr', 'Serbian'),
        ('sk', 'Slovak'),
        ('sl', 'Slovenian'),
        ('et', 'Estonian'),
        ('lv', 'Latvian'),
        ('lt', 'Lithuanian'),
        ('uk', 'Ukrainian'),
        ('be', 'Belarusian'),
        ('ka', 'Georgian'),
        ('am', 'Amharic'),
        ('so', 'Somali'),
        ('ne', 'Nepali'),
        ('si', 'Sinhala'),
        ('my', 'Myanmar'),
        ('km', 'Khmer'),
        ('lo', 'Lao'),
        ('mn', 'Mongolian'),
        ('kk', 'Kazakh'),
        ('ky', 'Kyrgyz'),
        ('uz', 'Uzbek'),
        ('tg', 'Tajik'),
        ('tm', 'Turkmen'),
    ]
    
    code = models.CharField(max_length=10, choices=LANGUAGES, unique=True)
    name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_rtl = models.BooleanField(default=False)  # Right-to-left languages
    
    # Regional variations
    region = models.CharField(max_length=50, blank=True, help_text="e.g., US, UK, IN, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
    
    def __str__(self):
        return f"{self.name} ({self.code.upper()})"
    
    def get_display_name(self):
        """Get display name with native name if different"""
        if self.native_name != self.name:
            return f"{self.name} ({self.native_name})"
        return self.name


class Translation(models.Model):
    """Multi-language translations for system content"""
    
    CONTENT_TYPES = [
        ('ui_label', 'UI Label'),
        ('ui_message', 'UI Message'),
        ('error_message', 'Error Message'),
        ('email_template', 'Email Template'),
        ('report_template', 'Report Template'),
        ('form_field', 'Form Field'),
        ('help_text', 'Help Text'),
        ('notification', 'Notification'),
    ]
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    key = models.CharField(max_length=200)  # Translation key
    value = models.TextField()  # Translated text
    
    # Context
    context = models.CharField(max_length=200, blank=True, help_text="Context for translation")
    plural_form = models.TextField(blank=True, help_text="Plural form if applicable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['language', 'content_type', 'key']
        verbose_name = _('Translation')
        verbose_name_plural = _('Translations')
    
    def __str__(self):
        return f"{self.language.name} - {self.key}"


class SchoolLanguage(models.Model):
    """Languages supported by a specific school"""
    
    school = models.ForeignKey('core.School', on_delete=models.CASCADE, db_index=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    is_teaching_language = models.BooleanField(default=True)
    
    # Proficiency levels
    proficiency_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('native', 'Native'),
    ], default='intermediate')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'language']
        verbose_name = _('School Language')
        verbose_name_plural = _('School Languages')
    
    def __str__(self):
        return f"{self.school.name} - {self.language.name}"


class UserLanguage(models.Model):
    """User language preferences"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    is_preferred = models.BooleanField(default=False)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('native', 'Native'),
    ], default='native')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'language']
        verbose_name = _('User Language')
        verbose_name_plural = _('User Languages')
    
    def __str__(self):
        return f"{self.user.username} - {self.language.name}"


class GradeTranslation(models.Model):
    """Translations for grade names and levels"""
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    original_grade = models.CharField(max_length=50)  # e.g., "Grade 1", "Form 1"
    translated_grade = models.CharField(max_length=50)
    grade_level = models.IntegerField()  # Numeric level for sorting
    
    # Context
    school_type = models.CharField(max_length=50, blank=True)
    curriculum_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['language', 'original_grade', 'grade_level']
        verbose_name = _('Grade Translation')
        verbose_name_plural = _('Grade Translations')
    
    def __str__(self):
        return f"{self.original_grade} → {self.translated_grade} ({self.language.name})"


class SubjectTranslation(models.Model):
    """Translations for subject names"""
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    original_subject = models.CharField(max_length=200)
    translated_subject = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=20)
    
    # Context
    curriculum_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['language', 'original_subject', 'subject_code']
        verbose_name = _('Subject Translation')
        verbose_name_plural = _('Subject Translations')
    
    def __str__(self):
        return f"{self.original_subject} → {self.translated_subject} ({self.language.name})"
