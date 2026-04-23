from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_display', 'enrolled_at', 'last_accessed_at')
    list_filter = ('status', 'enrolled_at', 'course__category')
    search_fields = ('student__email', 'student__username', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at', 'last_accessed_at')
    date_hierarchy = 'enrolled_at'

    def progress_display(self, obj):
        return f"{obj.progress_percentage}%"
    progress_display.short_description = 'Progression'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at', 'updated_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('enrollment__student__email', 'lesson__title')
    readonly_fields = ('created_at', 'updated_at')