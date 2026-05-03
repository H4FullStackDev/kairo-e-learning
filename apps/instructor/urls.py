from django.urls import path
from . import views

app_name = 'instructor'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Cours
    path('cours/', views.CourseListView.as_view(), name='course_list'),
    path('cours/nouveau/', views.CourseCreateView.as_view(), name='course_create'),
    path('cours/<int:pk>/', views.CourseManageView.as_view(), name='course_manage'),
    path('cours/<int:pk>/editer/', views.CourseEditView.as_view(), name='course_edit'),
    path('cours/<int:pk>/supprimer/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('cours/<int:pk>/publier/', views.toggle_course_status, name='course_toggle_status'),

    # Chapitres
    path('cours/<int:course_id>/chapitres/nouveau/', views.ChapterCreateView.as_view(), name='chapter_create'),
    path('chapitres/<int:pk>/editer/', views.ChapterEditView.as_view(), name='chapter_edit'),
    path('chapitres/<int:pk>/supprimer/', views.ChapterDeleteView.as_view(), name='chapter_delete'),
    path('chapitres/reordonner/', views.reorder_chapters, name='chapter_reorder'),

    # Leçons
    path('chapitres/<int:chapter_id>/lecons/nouvelle/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lecons/<int:pk>/editer/', views.LessonEditView.as_view(), name='lesson_edit'),
    path('lecons/<int:pk>/supprimer/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    path('lecons/reordonner/', views.reorder_lessons, name='lesson_reorder'),

    # Quiz
    path('cours/<int:course_id>/quiz/', views.QuizListView.as_view(), name='quiz_list'),
    path('cours/<int:course_id>/quiz/nouveau/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('quiz/<int:pk>/', views.QuizManageView.as_view(), name='quiz_manage'),
    path('quiz/<int:pk>/editer/', views.QuizEditView.as_view(), name='quiz_edit'),
    path('quiz/<int:pk>/supprimer/', views.QuizDeleteView.as_view(), name='quiz_delete'),

    # Questions (sous-éléments d'un quiz)
    path('quiz/<int:quiz_id>/questions/nouvelle/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/editer/', views.QuestionEditView.as_view(), name='question_edit'),
    path('questions/<int:pk>/supprimer/', views.delete_question, name='question_delete'),

    # Étudiants
    path('etudiants/', views.StudentsView.as_view(), name='students'),
    path('cours/<int:course_id>/etudiants/', views.CourseStudentsView.as_view(), name='course_students'),

    # Statistiques
    path('cours/<int:pk>/statistiques/', views.CourseStatsView.as_view(), name='course_stats'),
]