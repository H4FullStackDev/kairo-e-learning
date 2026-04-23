from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('mes-cours/', views.MyCoursesView.as_view(), name='my_courses'),
    path('inscription/<slug:course_slug>/', views.enroll_in_course, name='enroll'),
    path('cours/<slug:course_slug>/lecon/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('api/lecon/<int:lesson_id>/toggle/', views.toggle_lesson_completion, name='toggle_lesson'),
]