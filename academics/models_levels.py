"""
Configurable Education Levels System
Allows each school to define their own grade/level structure
"""

from django.db import models
from core.models import School
from core.managers import TenantAwareModel


class EducationLevel(TenantAwareModel):
    """
    Flexible education level system - configurable per school
    Replaces hardcoded Grade model
    """
    LEVEL_TYPE_CHOICES = [
        ('early_years', 'Early Years'),
        ('primary', 'Primary/Elementary'),
        ('lower_secondary', 'Lower Secondary/Middle School'),
        ('upper_secondary', 'Upper Secondary/High School'),
        ('vocational', 'Vocational/Technical'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('doctorate', 'Doctorate'),
        ('professional', 'Professional'),
        ('alternative', 'Alternative/Specialized'),
        ('custom', 'Custom'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='education_levels', db_index=True)
    
    # Basic Info
    name = models.CharField(max_length=100, db_index=True, help_text="e.g., Grade 1, Year 7, Form 3, Bachelor's")
    level_type = models.CharField(max_length=30, choices=LEVEL_TYPE_CHOICES, db_index=True)
    order = models.IntegerField(help_text="Sequence order (1, 2, 3...)")
    
    # Optional Details
    code = models.CharField(max_length=20, blank=True, help_text="e.g., G1, Y7, F3")
    description = models.TextField(blank=True)
    age_range = models.CharField(max_length=50, blank=True, help_text="e.g., 6-7 years, 18-22 years")
    
    # Capacity & Settings
    capacity = models.IntegerField(default=40, help_text="Default class size")
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['school', 'order']
        indexes = [
            models.Index(fields=['school', 'level_type', 'is_active']),
            models.Index(fields=['school', 'order']),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class LevelPreset(models.Model):
    """
    Predefined level templates for quick setup
    Not tenant-aware - these are global templates
    """
    name = models.CharField(max_length=100, unique=True, help_text="e.g., UK System, US System, IB System")
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['country', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name


class LevelPresetItem(models.Model):
    """
    Individual levels within a preset
    """
    preset = models.ForeignKey(LevelPreset, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    level_type = models.CharField(max_length=30, choices=EducationLevel.LEVEL_TYPE_CHOICES)
    order = models.IntegerField()
    code = models.CharField(max_length=20, blank=True)
    age_range = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['preset', 'order']
        unique_together = ['preset', 'order']
    
    def __str__(self):
        return f"{self.preset.name} - {self.name}"
