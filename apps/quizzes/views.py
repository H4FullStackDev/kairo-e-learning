from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, View, ListView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer


@login_required
def start_quiz(request, quiz_id):
    """Démarre une tentative de quiz."""
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)

    # Vérifier l'inscription au cours
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=quiz.course
    ).first()

    if not enrollment:
        messages.error(request, "Vous devez être inscrit au cours pour faire le quiz.")
        return redirect('courses:course_detail', slug=quiz.course.slug)

    # Vérifier nombre de tentatives
    attempts_count = QuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz,
        status=QuizAttempt.Status.COMPLETED
    ).count()

    if quiz.max_attempts > 0 and attempts_count >= quiz.max_attempts:
        messages.warning(request, f"Vous avez atteint le nombre maximum de tentatives ({quiz.max_attempts}).")
        return redirect('quizzes:quiz_results_list', course_slug=quiz.course.slug, quiz_id=quiz.id)

    # Fermer les tentatives en cours
    QuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz,
        status=QuizAttempt.Status.IN_PROGRESS
    ).update(status=QuizAttempt.Status.ABANDONED)

    # Créer une nouvelle tentative
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
    )

    return redirect('quizzes:quiz_take', attempt_id=attempt.id)


class QuizTakeView(LoginRequiredMixin, DetailView):
    """Vue pour passer un quiz."""
    model = QuizAttempt
    template_name = 'quizzes/quiz_take.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'

    def dispatch(self, request, *args, **kwargs):
        self.attempt = get_object_or_404(QuizAttempt, pk=kwargs.get('attempt_id'))

        # Seul le propriétaire peut voir sa tentative
        if self.attempt.student != request.user:
            messages.error(request, "Accès refusé.")
            return redirect('accounts:home')

        # Rediriger vers les résultats si déjà terminé
        if self.attempt.status == QuizAttempt.Status.COMPLETED:
            return redirect('quizzes:quiz_result', attempt_id=self.attempt.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.attempt.quiz
        context['questions'] = self.attempt.quiz.questions.prefetch_related('answers').all()
        context['course'] = self.attempt.quiz.course
        return context


@login_required
@require_POST
def submit_quiz(request, attempt_id):
    """Soumet les réponses du quiz."""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, student=request.user)

    if attempt.status == QuizAttempt.Status.COMPLETED:
        return redirect('quizzes:quiz_result', attempt_id=attempt.id)

    # Supprimer les anciennes réponses (au cas où)
    attempt.user_answers.all().delete()

    # Enregistrer les réponses
    for question in attempt.quiz.questions.all():
        field_name = f'question_{question.id}'

        if question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
            answer_ids = request.POST.getlist(field_name)
        else:
            answer_id = request.POST.get(field_name)
            answer_ids = [answer_id] if answer_id else []

        for aid in answer_ids:
            try:
                answer = Answer.objects.get(pk=aid, question=question)
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    answer=answer
                )
            except Answer.DoesNotExist:
                continue

    # Calculer le score
    attempt.calculate_score()

    return redirect('quizzes:quiz_result', attempt_id=attempt.id)


class QuizResultView(LoginRequiredMixin, DetailView):
    """Affichage des résultats d'un quiz."""
    model = QuizAttempt
    template_name = 'quizzes/quiz_result.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'

    def dispatch(self, request, *args, **kwargs):
        attempt = get_object_or_404(QuizAttempt, pk=kwargs.get('attempt_id'))
        if attempt.student != request.user:
            messages.error(request, "Accès refusé.")
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object

        # Construire les résultats par question
        questions_with_results = []
        for question in attempt.quiz.questions.prefetch_related('answers').all():
            user_answer_ids = set(
                attempt.user_answers.filter(question=question).values_list('answer_id', flat=True)
            )
            correct_answer_ids = set(question.correct_answers.values_list('id', flat=True))

            answers_with_state = []
            for answer in question.answers.all():
                state = None
                if answer.id in user_answer_ids and answer.id in correct_answer_ids:
                    state = 'correct'
                elif answer.id in user_answer_ids and answer.id not in correct_answer_ids:
                    state = 'wrong'
                elif answer.id not in user_answer_ids and answer.id in correct_answer_ids:
                    state = 'missed'
                answers_with_state.append({'answer': answer, 'state': state, 'was_selected': answer.id in user_answer_ids})

            is_question_correct = user_answer_ids == correct_answer_ids and len(user_answer_ids) > 0

            questions_with_results.append({
                'question': question,
                'answers': answers_with_state,
                'is_correct': is_question_correct,
                'was_answered': len(user_answer_ids) > 0,
            })

        context['questions_with_results'] = questions_with_results
        context['quiz'] = attempt.quiz
        context['course'] = attempt.quiz.course

        # Nombre de tentatives restantes
        attempts_count = QuizAttempt.objects.filter(
            student=self.request.user,
            quiz=attempt.quiz,
            status=QuizAttempt.Status.COMPLETED
        ).count()
        if attempt.quiz.max_attempts > 0:
            context['attempts_remaining'] = max(0, attempt.quiz.max_attempts - attempts_count)
        else:
            context['attempts_remaining'] = None

        return context


class QuizResultsListView(LoginRequiredMixin, ListView):
    """Liste des tentatives d'un quiz pour un utilisateur."""
    template_name = 'quizzes/quiz_results_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'])
        return QuizAttempt.objects.filter(
            student=self.request.user,
            quiz=self.quiz,
            status=QuizAttempt.Status.COMPLETED
        ).order_by('-started_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        context['course'] = self.quiz.course
        context['best_attempt'] = self.get_queryset().order_by('-percentage').first()
        return context