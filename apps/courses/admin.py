from django.contrib import admin
from .models import Category, Course, Chapter, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'courses_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('title', 'order', 'description')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'price', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'level', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'instructor__email', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    inlines = [ChapterInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Relations', {
            'fields': ('instructor', 'category')
        }),
        ('Média', {
            'fields': ('thumbnail', 'trailer_video')
        }),
        ('Paramètres', {
            'fields': ('level', 'price', 'duration_hours', 'language')
        }),
        ('Contenu pédagogique', {
            'fields': ('objectives', 'prerequisites'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('status', 'is_featured')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'content_type', 'duration_minutes', 'is_free_preview')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'total_lessons', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'content_type', 'order', 'duration_minutes', 'is_free_preview')
    list_filter = ('content_type', 'is_free_preview', 'chapter__course')
    search_fields = ('title', 'chapter__title', 'chapter__course__title')
    prepopulated_fields = {'slug': ('title',)}