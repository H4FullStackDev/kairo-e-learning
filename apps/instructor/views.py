from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .mixins import InstructorRequiredMixin, CourseOwnerMixin
from .forms import CourseForm
from apps.courses.models import Course, Lesson, Chapter, Category
from apps.enrollments.models import Enrollment
from apps.quizzes.models import QuizAttempt, Quiz, Question 
from apps.certificates.models import Certificate
from apps.interactions.models import Comment


# ============================
# DASHBOARD
# ============================

class DashboardView(InstructorRequiredMixin, TemplateView):
    template_name = 'instructor/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        my_courses = Course.objects.filter(instructor=user)

        # Stats principales
        total_courses = my_courses.count()
        published_courses = my_courses.filter(status=Course.Status.PUBLISHED).count()
        total_students = Enrollment.objects.filter(
            course__instructor=user
        ).values('student').distinct().count()
        total_enrollments = Enrollment.objects.filter(course__instructor=user).count()
        total_certificates = Certificate.objects.filter(course__instructor=user).count()
        total_comments = Comment.objects.filter(
            lesson__chapter__course__instructor=user
        ).count()

        # Tendances
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        enrollments_this_month = Enrollment.objects.filter(
            course__instructor=user, enrolled_at__gte=thirty_days_ago
        ).count()
        enrollments_last_month = Enrollment.objects.filter(
            course__instructor=user,
            enrolled_at__gte=sixty_days_ago,
            enrolled_at__lt=thirty_days_ago
        ).count()
        if enrollments_last_month > 0:
            enrollment_trend = ((enrollments_this_month - enrollments_last_month) / enrollments_last_month) * 100
        else:
            enrollment_trend = 100 if enrollments_this_month > 0 else 0

        # Top cours
        top_courses = my_courses.annotate(
            enrollments_count=Count('enrollments', distinct=True),
            comments_count=Count('chapters__lessons__comments', distinct=True),
        ).order_by('-enrollments_count')[:5]

        # Activité
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_enrollments = Enrollment.objects.filter(
            course__instructor=user, enrolled_at__gte=seven_days_ago
        ).select_related('student', 'course').order_by('-enrolled_at')[:8]

        recent_comments = Comment.objects.filter(
            lesson__chapter__course__instructor=user
        ).exclude(author=user).select_related(
            'author', 'lesson__chapter__course'
        ).order_by('-created_at')[:5]

        # Quiz
        recent_quiz_attempts = QuizAttempt.objects.filter(
            quiz__course__instructor=user, status='COMPLETED'
        ).count()
        avg_quiz_score = QuizAttempt.objects.filter(
            quiz__course__instructor=user, status='COMPLETED'
        ).aggregate(avg=Avg('percentage'))['avg'] or 0

        context.update({
            'total_courses': total_courses,
            'published_courses': published_courses,
            'draft_courses': total_courses - published_courses,
            'total_students': total_students,
            'total_enrollments': total_enrollments,
            'total_certificates': total_certificates,
            'total_comments': total_comments,
            'recent_quiz_attempts': recent_quiz_attempts,
            'avg_quiz_score': round(avg_quiz_score, 1),
            'enrollments_this_month': enrollments_this_month,
            'enrollment_trend': round(enrollment_trend, 1),
            'enrollment_trend_up': enrollment_trend >= 0,
            'top_courses': top_courses,
            'recent_enrollments': recent_enrollments,
            'recent_comments': recent_comments,
            'my_courses': my_courses[:5],
        })
        return context


# ============================
# COURS - CRUD
# ============================

class CourseListView(InstructorRequiredMixin, ListView):
    """Liste tous les cours du formateur."""
    template_name = 'instructor/courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.filter(instructor=user).select_related('category').annotate(
            enrollments_count=Count('enrollments', distinct=True),
            chapters_count=Count('chapters', distinct=True),
            lessons_count=Count('chapters__lessons', distinct=True),
        )

        # Filtres
        status = self.request.GET.get('status')
        if status in ('PUBLISHED', 'DRAFT'):
            queryset = queryset.filter(status=status)

        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        all_courses = Course.objects.filter(instructor=user)
        context['stats'] = {
            'all': all_courses.count(),
            'published': all_courses.filter(status=Course.Status.PUBLISHED).count(),
            'draft': all_courses.filter(status=Course.Status.DRAFT).count(),
        }
        context['current_status'] = self.request.GET.get('status', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CourseCreateView(InstructorRequiredMixin, CreateView):
    """Création d'un nouveau cours."""
    model = Course
    form_class = CourseForm
    template_name = 'instructor/courses/course_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        # Le slug est auto-généré par le modèle
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Le cours « {self.object.title} » a été créé avec succès. "
            "Ajoutez maintenant des chapitres et des leçons."
        )
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        context['page_title'] = 'Nouveau cours'
        return context


class CourseEditView(InstructorRequiredMixin, CourseOwnerMixin, UpdateView):
    """Édition d'un cours existant."""
    model = Course
    form_class = CourseForm
    template_name = 'instructor/courses/course_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Le cours « {self.object.title} » a été mis à jour.")
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['page_title'] = f"Éditer · {self.object.title}"
        return context


class CourseManageView(InstructorRequiredMixin, CourseOwnerMixin, DetailView):
    """Page de gestion d'un cours (chapitres, leçons, paramètres)."""
    model = Course
    template_name = 'instructor/courses/course_manage.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        # Chapitres avec leçons préchargées
        chapters = course.chapters.prefetch_related('lessons').order_by('order')

        # Stats du cours
        total_lessons = Lesson.objects.filter(chapter__course=course).count()
        total_enrollments = course.enrollments.count()
        active_enrollments = course.enrollments.filter(status=Enrollment.Status.ACTIVE).count()
        completed_enrollments = course.enrollments.filter(status=Enrollment.Status.COMPLETED).count()
        total_certificates = Certificate.objects.filter(course=course).count()
        total_quizzes = Quiz.objects.filter(course=course).count()
        total_comments = Comment.objects.filter(lesson__chapter__course=course).count()

        context.update({
            'chapters': chapters,
            'total_chapters': chapters.count(),
            'total_lessons': total_lessons,
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'completed_enrollments': completed_enrollments,
            'total_certificates': total_certificates,
            'total_quizzes': total_quizzes,
            'total_comments': total_comments,
        })
        return context


class CourseDeleteView(InstructorRequiredMixin, CourseOwnerMixin, DeleteView):
    """Suppression d'un cours avec confirmation."""
    model = Course
    template_name = 'instructor/courses/course_confirm_delete.html'
    success_url = reverse_lazy('instructor:course_list')
    context_object_name = 'course'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        messages.success(request, f"Le cours « {title} » a été définitivement supprimé.")
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def toggle_course_status(request, pk):
    """Bascule rapide entre Brouillon et Publié."""
    course = get_object_or_404(Course, pk=pk)

    if course.instructor != request.user and not request.user.is_superuser:
        messages.error(request, "Action non autorisée.")
        return redirect('instructor:course_list')

    if course.status == Course.Status.PUBLISHED:
        course.status = Course.Status.DRAFT
        messages.info(request, f"« {course.title} » a été dépublié.")
    else:
        # Vérifier qu'il y a au moins un chapitre avant de publier
        if not course.chapters.exists():
            messages.warning(request, "Vous devez ajouter au moins un chapitre avant de publier le cours.")
            return redirect('instructor:course_manage', pk=course.pk)

        course.status = Course.Status.PUBLISHED
        course.published_at = timezone.now()
        messages.success(request, f"« {course.title} » est maintenant publié et visible par tous !")

    course.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('instructor:course_list')))

# ============================
# CHAPITRES - CRUD
# ============================

class ChapterCreateView(InstructorRequiredMixin, CreateView):
    """Création d'un chapitre dans un cours."""
    model = Chapter
    form_class = None  # défini dans get_form_class
    template_name = 'instructor/chapters/chapter_form.html'

    def get_form_class(self):
        from .forms import ChapterForm
        return ChapterForm

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['course_id'])
        # Vérifier que l'utilisateur est bien le formateur
        if self.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        # Pré-remplir l'ordre avec le suivant disponible
        last_order = Chapter.objects.filter(course=self.course).count()
        return {'order': last_order + 1}

    def form_valid(self, form):
        form.instance.course = self.course
        response = super().form_valid(form)
        messages.success(self.request, f"Chapitre « {self.object.title} » créé.")
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['is_create'] = True
        context['page_title'] = 'Nouveau chapitre'
        return context


class ChapterEditView(InstructorRequiredMixin, UpdateView):
    """Édition d'un chapitre."""
    model = Chapter
    form_class = None
    template_name = 'instructor/chapters/chapter_form.html'

    def get_form_class(self):
        from .forms import ChapterForm
        return ChapterForm

    def dispatch(self, request, *args, **kwargs):
        chapter = get_object_or_404(Chapter, pk=kwargs['pk'])
        if chapter.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Chapitre mis à jour.")
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.object.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['is_create'] = False
        context['page_title'] = f"Éditer · {self.object.title}"
        return context


class ChapterDeleteView(InstructorRequiredMixin, DeleteView):
    """Suppression d'un chapitre."""
    model = Chapter
    template_name = 'instructor/chapters/chapter_confirm_delete.html'
    context_object_name = 'chapter'

    def dispatch(self, request, *args, **kwargs):
        chapter = get_object_or_404(Chapter, pk=kwargs['pk'])
        if chapter.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f"Chapitre supprimé.")
        return reverse('instructor:course_manage', kwargs={'pk': self.object.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


@login_required
@require_POST
def reorder_chapters(request):
    """Réordonner les chapitres via AJAX (drag & drop)."""
    import json
    try:
        data = json.loads(request.body)
        chapter_ids = data.get('chapter_ids', [])

        for index, chapter_id in enumerate(chapter_ids, start=1):
            try:
                chapter = Chapter.objects.get(pk=chapter_id)
                if chapter.course.instructor == request.user or request.user.is_superuser:
                    chapter.order = index
                    chapter.save(update_fields=['order'])
            except Chapter.DoesNotExist:
                continue

        from django.http import JsonResponse
        return JsonResponse({'success': True})
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': str(e)}, status=400)


# ============================
# LECONS - CRUD
# ============================

class LessonCreateView(InstructorRequiredMixin, CreateView):
    """Création d'une leçon dans un chapitre."""
    model = Lesson
    form_class = None
    template_name = 'instructor/lessons/lesson_form.html'

    def get_form_class(self):
        from .forms import LessonForm
        return LessonForm

    def dispatch(self, request, *args, **kwargs):
        self.chapter = get_object_or_404(Chapter, pk=kwargs['chapter_id'])
        if self.chapter.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        last_order = Lesson.objects.filter(chapter=self.chapter).count()
        return {'order': last_order + 1, 'duration_minutes': 15}

    def form_valid(self, form):
        form.instance.chapter = self.chapter
        response = super().form_valid(form)
        messages.success(self.request, f"Leçon « {self.object.title} » créée.")
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.chapter.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter'] = self.chapter
        context['course'] = self.chapter.course
        context['is_create'] = True
        context['page_title'] = 'Nouvelle leçon'
        return context


class LessonEditView(InstructorRequiredMixin, UpdateView):
    """Édition d'une leçon."""
    model = Lesson
    form_class = None
    template_name = 'instructor/lessons/lesson_form.html'

    def get_form_class(self):
        from .forms import LessonForm
        return LessonForm

    def dispatch(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=kwargs['pk'])
        if lesson.chapter.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Leçon mise à jour.")
        return response

    def get_success_url(self):
        return reverse('instructor:course_manage', kwargs={'pk': self.object.chapter.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter'] = self.object.chapter
        context['course'] = self.object.chapter.course
        context['is_create'] = False
        context['page_title'] = f"Éditer · {self.object.title}"
        return context


class LessonDeleteView(InstructorRequiredMixin, DeleteView):
    """Suppression d'une leçon."""
    model = Lesson
    template_name = 'instructor/lessons/lesson_confirm_delete.html'
    context_object_name = 'lesson'

    def dispatch(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=kwargs['pk'])
        if lesson.chapter.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f"Leçon supprimée.")
        return reverse('instructor:course_manage', kwargs={'pk': self.object.chapter.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter'] = self.object.chapter
        context['course'] = self.object.chapter.course
        return context


@login_required
@require_POST
def reorder_lessons(request):
    """Réordonner les leçons via AJAX."""
    import json
    try:
        data = json.loads(request.body)
        lesson_ids = data.get('lesson_ids', [])

        for index, lesson_id in enumerate(lesson_ids, start=1):
            try:
                lesson = Lesson.objects.get(pk=lesson_id)
                if lesson.chapter.course.instructor == request.user or request.user.is_superuser:
                    lesson.order = index
                    lesson.save(update_fields=['order'])
            except Lesson.DoesNotExist:
                continue

        from django.http import JsonResponse
        return JsonResponse({'success': True})
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': str(e)}, status=400)
    
# ============================
# QUIZ - CRUD
# ============================

class QuizListView(InstructorRequiredMixin, ListView):
    """Liste des quiz d'un cours."""
    template_name = 'instructor/quizzes/quiz_list.html'
    context_object_name = 'quizzes'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['course_id'])
        if self.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Quiz.objects.filter(course=self.course).annotate(
            questions_count=Count('questions'),
            attempts_count=Count('attempts'),
        ).order_by('quiz_type', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context


class QuizCreateView(InstructorRequiredMixin, CreateView):
    """Création d'un quiz."""
    model = Quiz
    template_name = 'instructor/quizzes/quiz_form.html'

    def get_form_class(self):
        from .forms import QuizForm
        return QuizForm

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['course_id'])
        if self.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.course
        return kwargs

    def form_valid(self, form):
        form.instance.course = self.course
        response = super().form_valid(form)
        messages.success(self.request, f"Quiz « {self.object.title} » créé. Ajoutez maintenant des questions.")
        return response

    def get_success_url(self):
        return reverse('instructor:quiz_manage', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['is_create'] = True
        return context


class QuizManageView(InstructorRequiredMixin, DetailView):
    """Page de gestion d'un quiz (questions et statistiques)."""
    model = Quiz
    template_name = 'instructor/quizzes/quiz_manage.html'
    context_object_name = 'quiz'

    def dispatch(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs['pk'])
        if quiz.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object

        questions = quiz.questions.prefetch_related('answers').order_by('order')

        # Stats
        attempts = QuizAttempt.objects.filter(quiz=quiz, status='COMPLETED')
        total_attempts = attempts.count()
        passed_attempts = attempts.filter(is_passed=True).count()
        pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0

        context.update({
            'questions': questions,
            'course': quiz.course,
            'total_questions': questions.count(),
            'total_points': sum(q.points for q in questions),
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'pass_rate': round(pass_rate, 1),
            'avg_score': round(avg_score, 1),
        })
        return context


class QuizEditView(InstructorRequiredMixin, UpdateView):
    """Édition d'un quiz."""
    model = Quiz
    template_name = 'instructor/quizzes/quiz_form.html'

    def get_form_class(self):
        from .forms import QuizForm
        return QuizForm

    def dispatch(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs['pk'])
        if quiz.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.object.course
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Quiz mis à jour.")
        return response

    def get_success_url(self):
        return reverse('instructor:quiz_manage', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['is_create'] = False
        return context


class QuizDeleteView(InstructorRequiredMixin, DeleteView):
    """Suppression d'un quiz."""
    model = Quiz
    template_name = 'instructor/quizzes/quiz_confirm_delete.html'
    context_object_name = 'quiz'

    def dispatch(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs['pk'])
        if quiz.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Quiz supprimé.")
        return reverse('instructor:quiz_list', kwargs={'course_id': self.object.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


# ============================
# QUESTIONS - CRUD
# ============================

class QuestionCreateView(InstructorRequiredMixin, CreateView):
    """Création d'une question avec ses réponses."""
    model = Question
    template_name = 'instructor/quizzes/question_form.html'

    def get_form_class(self):
        from .forms import QuestionForm
        return QuestionForm

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=kwargs['quiz_id'])
        if self.quiz.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        last_order = Question.objects.filter(quiz=self.quiz).count()
        return {'order': last_order + 1, 'points': 1}

    def post(self, request, *args, **kwargs):
        from .forms import QuestionForm
        form = QuestionForm(request.POST)

        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = self.quiz
            question.save()

            # Créer les réponses depuis les champs dynamiques
            answer_texts = request.POST.getlist('answer_text')
            answer_corrects = request.POST.getlist('answer_correct')

            for i, text in enumerate(answer_texts):
                if text.strip():
                    Answer.objects.create(
                        question=question,
                        text=text.strip(),
                        is_correct=str(i) in answer_corrects,
                        order=i + 1,
                    )

            messages.success(request, "Question créée avec ses réponses.")
            return redirect('instructor:quiz_manage', pk=self.quiz.pk)

        # Si erreur de form
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        context['course'] = self.quiz.course
        context['is_create'] = True
        return context


class QuestionEditView(InstructorRequiredMixin, UpdateView):
    """Édition d'une question."""
    model = Question
    template_name = 'instructor/quizzes/question_form.html'

    def get_form_class(self):
        from .forms import QuestionForm
        return QuestionForm

    def dispatch(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs['pk'])
        if question.quiz.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from .forms import QuestionForm
        self.object = self.get_object()
        form = QuestionForm(request.POST, instance=self.object)

        if form.is_valid():
            question = form.save()

            # Recréer les réponses
            question.answers.all().delete()
            answer_texts = request.POST.getlist('answer_text')
            answer_corrects = request.POST.getlist('answer_correct')

            for i, text in enumerate(answer_texts):
                if text.strip():
                    Answer.objects.create(
                        question=question,
                        text=text.strip(),
                        is_correct=str(i) in answer_corrects,
                        order=i + 1,
                    )

            messages.success(request, "Question mise à jour.")
            return redirect('instructor:quiz_manage', pk=question.quiz.pk)

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.object.quiz
        context['course'] = self.object.quiz.course
        context['is_create'] = False
        context['existing_answers'] = self.object.answers.order_by('order')
        return context


@login_required
@require_POST
def delete_question(request, pk):
    """Supprime une question."""
    question = get_object_or_404(Question, pk=pk)
    if question.quiz.course.instructor != request.user and not request.user.is_superuser:
        messages.error(request, "Action non autorisée.")
        return redirect('instructor:course_list')

    quiz_id = question.quiz.pk
    question.delete()
    messages.success(request, "Question supprimée.")
    return redirect('instructor:quiz_manage', pk=quiz_id)


# ============================
# ÉTUDIANTS
# ============================

class StudentsView(InstructorRequiredMixin, TemplateView):
    """Liste de tous les étudiants inscrits aux cours du formateur."""
    template_name = 'instructor/students/students_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Récupérer toutes les inscriptions des cours du formateur
        enrollments = Enrollment.objects.filter(
            course__instructor=user
        ).select_related('student', 'course').order_by('-enrolled_at')

        # Filtre par cours
        course_filter = self.request.GET.get('course')
        if course_filter:
            enrollments = enrollments.filter(course_id=course_filter)

        # Filtre par statut
        status_filter = self.request.GET.get('status')
        if status_filter in ('ACTIVE', 'COMPLETED'):
            enrollments = enrollments.filter(status=status_filter)

        # Recherche
        search = self.request.GET.get('q', '').strip()
        if search:
            enrollments = enrollments.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__email__icontains=search)
            )

        context.update({
            'enrollments': enrollments,
            'my_courses': Course.objects.filter(instructor=user),
            'course_filter': course_filter,
            'status_filter': status_filter or 'all',
            'search_query': search,
            'total_students': enrollments.values('student').distinct().count(),
            'active_count': enrollments.filter(status='ACTIVE').count(),
            'completed_count': enrollments.filter(status='COMPLETED').count(),
        })
        return context


class CourseStudentsView(InstructorRequiredMixin, ListView):
    """Liste détaillée des étudiants d'un cours spécifique."""
    template_name = 'instructor/students/course_students.html'
    context_object_name = 'enrollments'
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['course_id'])
        if self.course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Enrollment.objects.filter(
            course=self.course
        ).select_related('student').order_by('-enrolled_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context


# ============================
# STATISTIQUES
# ============================

class CourseStatsView(InstructorRequiredMixin, DetailView):
    """Statistiques détaillées d'un cours."""
    model = Course
    template_name = 'instructor/courses/course_stats.html'
    context_object_name = 'course'

    def dispatch(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=kwargs['pk'])
        if course.instructor != request.user and not request.user.is_superuser:
            messages.error(request, "Action non autorisée.")
            return redirect('instructor:course_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        # Inscriptions
        enrollments = Enrollment.objects.filter(course=course)
        total_enrollments = enrollments.count()
        active_count = enrollments.filter(status='ACTIVE').count()
        completed_count = enrollments.filter(status='COMPLETED').count()
        completion_rate = (completed_count / total_enrollments * 100) if total_enrollments > 0 else 0

        # Évolution sur 30 jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        enrollments_by_day = []
        for i in range(30, 0, -1):
            day = timezone.now() - timedelta(days=i)
            count = enrollments.filter(
                enrolled_at__date=day.date()
            ).count()
            enrollments_by_day.append({
                'date': day.strftime('%d/%m'),
                'count': count,
            })

        # Quiz stats
        quizzes = Quiz.objects.filter(course=course)
        quiz_stats = []
        for quiz in quizzes:
            attempts = QuizAttempt.objects.filter(quiz=quiz, status='COMPLETED')
            quiz_stats.append({
                'quiz': quiz,
                'attempts': attempts.count(),
                'pass_rate': (attempts.filter(is_passed=True).count() / attempts.count() * 100) if attempts.count() > 0 else 0,
                'avg_score': attempts.aggregate(avg=Avg('percentage'))['avg'] or 0,
            })

        # Certificats
        total_certificates = Certificate.objects.filter(course=course).count()

        # Commentaires
        total_comments = Comment.objects.filter(lesson__chapter__course=course).count()
        instructor_replies = Comment.objects.filter(
            lesson__chapter__course=course,
            is_instructor_reply=True
        ).count()

        context.update({
            'total_enrollments': total_enrollments,
            'active_count': active_count,
            'completed_count': completed_count,
            'completion_rate': round(completion_rate, 1),
            'enrollments_by_day': enrollments_by_day,
            'quiz_stats': quiz_stats,
            'total_certificates': total_certificates,
            'total_comments': total_comments,
            'instructor_replies': instructor_replies,
        })
        return context