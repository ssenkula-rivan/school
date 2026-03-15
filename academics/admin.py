from django.contrib import admin
from .models import (
    Subject, ClassSubject, Timetable, Exam, GradeScale, GradeScaleRange,
    Mark, ReportCard, StudentAttendance, StudentPromotion
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'level', 'credit_hours', 'is_active']
    list_filter = ['category', 'level', 'is_active']
    search_fields = ['code', 'name']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['grade', 'subject', 'teacher', 'academic_year', 'periods_per_week']
    list_filter = ['academic_year', 'grade']
    search_fields = ['subject__name', 'teacher__username']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_subject', 'day_of_week', 'start_time', 'end_time', 'room_number']
    list_filter = ['day_of_week']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'term', 'grade', 'start_date', 'is_published']
    list_filter = ['exam_type', 'term', 'academic_year', 'is_published']
    search_fields = ['name']


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'is_default']
    list_filter = ['level', 'is_default']


@admin.register(GradeScaleRange)
class GradeScaleRangeAdmin(admin.ModelAdmin):
    list_display = ['grade_scale', 'grade', 'min_percentage', 'max_percentage', 'grade_point']
    list_filter = ['grade_scale']


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam', 'marks_obtained', 'percentage', 'grade', 'grade_point']
    list_filter = ['exam', 'grade', 'is_absent']
    search_fields = ['student__first_name', 'student__last_name', 'subject__name']


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'average_percentage', 'gpa', 'overall_grade', 'class_rank', 'is_published']
    list_filter = ['academic_year', 'term', 'is_published']
    search_fields = ['student__first_name', 'student__last_name']
    actions = ['generate_report_cards']
    
    def generate_report_cards(self, request, queryset):
        for report in queryset:
            report.calculate_results()
        self.message_user(request, f'{queryset.count()} report cards generated successfully.')
    generate_report_cards.short_description = 'Generate/Update Report Cards'


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'date'


@admin.register(StudentPromotion)
class StudentPromotionAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_grade', 'to_grade', 'status', 'academic_year', 'promoted_at']
    list_filter = ['status', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name']
