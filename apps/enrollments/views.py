from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Prefetch

from apps.courses.models import Course, Chapter, Lesson
from .models import Enrollment, LessonProgress


@login_required
@require_POST
def enroll_in_course(request, course_slug):
    """Inscrit un utilisateur à un cours."""
    course = get_object_or_404(Course, slug=course_slug, status=Course.Status.PUBLISHED)

    # Vérifier si déjà inscrit
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': Enrollment.Status.ACTIVE}
    )

    if created:
        messages.success(request, f"Inscription réussie à « {course.title} ». Bon apprentissage !")
    else:
        messages.info(request, f"Vous êtes déjà inscrit à ce cours.")

    # Redirection vers la première leçon ou le dashboard
    first_lesson = Lesson.objects.filter(chapter__course=course).order_by('chapter__order', 'order').first()
    if first_lesson:
        return redirect('enrollments:lesson_detail', course_slug=course.slug, lesson_id=first_lesson.id)
    return redirect('enrollments:my_courses')


class MyCoursesView(LoginRequiredMixin, ListView):
    """Dashboard étudiant : liste de mes cours."""
    template_name = 'enrollments/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 12

    def get_queryset(self):
        queryset = Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor', 'course__category').order_by('-last_accessed_at')

        # Filtre par statut
        status_filter = self.request.GET.get('status')
        if status_filter in ['ACTIVE', 'COMPLETED']:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_enrollments = Enrollment.objects.filter(student=self.request.user)
        context['total_count'] = all_enrollments.count()
        context['active_count'] = all_enrollments.filter(status=Enrollment.Status.ACTIVE).count()
        context['completed_count'] = all_enrollments.filter(status=Enrollment.Status.COMPLETED).count()
        context['current_status'] = self.request.GET.get('status', '')
        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    """Vue du lecteur de leçon."""
    model = Lesson
    template_name = 'enrollments/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs.get('course_slug'))
        self.lesson = get_object_or_404(Lesson, pk=kwargs.get('lesson_id'))

        # Vérifier que la leçon appartient bien à ce cours
        if self.lesson.chapter.course != self.course:
            messages.error(request, "Cette leçon n'appartient pas à ce cours.")
            return redirect('courses:course_detail', slug=self.course.slug)

        # Vérifier l'inscription OU l'aperçu gratuit
        self.enrollment = Enrollment.objects.filter(
            student=request.user,
            course=self.course
        ).first()

        if not self.enrollment and not self.lesson.is_free_preview:
            messages.warning(request, "Vous devez être inscrit pour accéder à cette leçon.")
            return redirect('courses:course_detail', slug=self.course.slug)

        # Récupérer ou créer la progression
        if self.enrollment:
            self.progress, _ = LessonProgress.objects.get_or_create(
                enrollment=self.enrollment,
                lesson=self.lesson
            )
        else:
            self.progress = None

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['enrollment'] = self.enrollment
        context['progress'] = self.progress

        # Tous les chapitres avec leçons préchargées
        chapters = Chapter.objects.filter(course=self.course).prefetch_related('lessons').order_by('order')

        # IDs des leçons terminées par l'utilisateur
        completed_lesson_ids = []
        if self.enrollment:
            completed_lesson_ids = list(LessonProgress.objects.filter(
                enrollment=self.enrollment,
                is_completed=True
            ).values_list('lesson_id', flat=True))

        context['chapters'] = chapters
        context['completed_lesson_ids'] = completed_lesson_ids

        # Navigation : leçon précédente / suivante
        all_lessons = list(Lesson.objects.filter(
            chapter__course=self.course
        ).order_by('chapter__order', 'order'))

        try:
            current_index = all_lessons.index(self.lesson)
            context['prev_lesson'] = all_lessons[current_index - 1] if current_index > 0 else None
            context['next_lesson'] = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
            context['current_lesson_number'] = current_index + 1
            context['total_lessons'] = len(all_lessons)
        except ValueError:
            context['prev_lesson'] = None
            context['next_lesson'] = None

        # Commentaires (racine uniquement, avec réponses préchargées)
        from apps.interactions.models import Comment
        context['lesson_comments'] = Comment.objects.filter(
            lesson=self.lesson,
            parent__isnull=True
        ).select_related('author').prefetch_related('replies__author', 'liked_by').order_by('-is_pinned', '-created_at')
        context['lesson_comments_count'] = Comment.objects.filter(lesson=self.lesson).count()

        return context


@login_required
@require_POST
def toggle_lesson_completion(request, lesson_id):
    """Marque/démarque une leçon comme terminée (AJAX)."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=lesson.chapter.course
    ).first()

    if not enrollment:
        return JsonResponse({'error': 'Non inscrit à ce cours'}, status=403)

    progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    if progress.is_completed:
        progress.mark_uncompleted()
        completed = False
    else:
        progress.mark_completed()
        completed = True

    return JsonResponse({
        'success': True,
        'is_completed': completed,
        'progress_percentage': enrollment.progress_percentage,
        'completed_lessons': enrollment.completed_lessons_count,
        'total_lessons': enrollment.total_lessons_count,
        'is_course_completed': enrollment.is_completed,
    })