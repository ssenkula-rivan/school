from django.contrib import admin
from .models import School, Department, AcademicYear, Grade, Student


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'school_type', 'is_active', 'subscription_end']
    list_filter = ['is_active', 'school_type', 'institution_type']
    search_fields = ['name', 'code', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'head', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'school__name']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'start_date', 'end_date', 'is_current']
    list_filter = ['school', 'is_current']
    search_fields = ['name', 'school__name']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'level', 'capacity']
    list_filter = ['school', 'level']
    search_fields = ['name', 'school__name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'get_full_name', 'school', 'grade', 'status']
    list_filter = ['school', 'status', 'grade', 'scholarship_status']
    search_fields = ['admission_number', 'first_name', 'last_name', 'school__name']
    readonly_fields = ['created_at', 'updated_at']
