from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='quiz_start'),
    path('tentative/<int:attempt_id>/', views.QuizTakeView.as_view(), name='quiz_take'),
    path('tentative/<int:attempt_id>/submit/', views.submit_quiz, name='quiz_submit'),
    path('tentative/<int:attempt_id>/resultat/', views.QuizResultView.as_view(), name='quiz_result'),
    path('cours/<slug:course_slug>/quiz/<int:quiz_id>/historique/', views.QuizResultsListView.as_view(), name='quiz_results_list'),
]