from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ('text', 'is_correct', 'order')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz')
    search_fields = ('text',)
    inlines = [AnswerInline]

    def text_short(self, obj):
        return obj.text[:80] + ('...' if len(obj.text) > 80 else '')
    text_short.short_description = 'Question'


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'order', 'explanation')
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'chapter', 'quiz_type', 'passing_score', 'total_questions', 'is_active')
    list_filter = ('quiz_type', 'is_active', 'course')
    search_fields = ('title', 'course__title')
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'percentage', 'is_passed', 'status', 'started_at')
    list_filter = ('status', 'is_passed', 'quiz')
    search_fields = ('student__email', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at', 'score', 'total_points', 'percentage', 'is_passed')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'answer')
    list_filter = ('attempt__quiz',)