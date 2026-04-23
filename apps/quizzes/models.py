from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.courses.models import Course, Chapter


class Quiz(models.Model):
    """Quiz associé à un cours ou chapitre."""

    class QuizType(models.TextChoices):
        COURSE_FINAL = 'COURSE_FINAL', _('Quiz final du cours')
        CHAPTER = 'CHAPTER', _('Quiz de chapitre')

    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name=_('Cours')
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True,
        verbose_name=_('Chapitre (optionnel)')
    )

    quiz_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=QuizType.choices,
        default=QuizType.CHAPTER
    )

    passing_score = models.PositiveIntegerField(
        _('Score de réussite (%)'),
        default=70,
        help_text=_('Score minimum pour réussir le quiz')
    )
    time_limit_minutes = models.PositiveIntegerField(
        _('Temps limite (min)'),
        default=0,
        help_text=_('0 = pas de limite')
    )
    max_attempts = models.PositiveIntegerField(
        _('Tentatives max'),
        default=3,
        help_text=_('0 = illimitées')
    )
    show_correct_answers = models.BooleanField(
        _('Afficher les bonnes réponses après'),
        default=True
    )
    is_active = models.BooleanField(_('Actif'), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quiz')
        ordering = ['course', 'chapter']

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """Question d'un quiz."""

    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = 'SINGLE', _('Choix unique')
        MULTIPLE_CHOICE = 'MULTIPLE', _('Choix multiples')
        TRUE_FALSE = 'TRUE_FALSE', _('Vrai / Faux')

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Quiz')
    )
    text = models.TextField(_('Énoncé de la question'))
    explanation = models.TextField(
        _('Explication (après réponse)'),
        blank=True,
        help_text=_('Affichée après la soumission pour aider à comprendre')
    )
    question_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE
    )
    points = models.PositiveIntegerField(_('Points'), default=1)
    order = models.PositiveIntegerField(_('Ordre'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"

    @property
    def correct_answers(self):
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """Réponse possible à une question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Question')
    )
    text = models.CharField(_('Texte de la réponse'), max_length=500)
    is_correct = models.BooleanField(_('Réponse correcte'), default=False)
    order = models.PositiveIntegerField(_('Ordre'), default=0)

    class Meta:
        verbose_name = _('Réponse')
        verbose_name_plural = _('Réponses')
        ordering = ['order']

    def __str__(self):
        marker = "✓" if self.is_correct else "✗"
        return f"{marker} {self.text[:50]}"


class QuizAttempt(models.Model):
    """Tentative d'un étudiant sur un quiz."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', _('En cours')
        COMPLETED = 'COMPLETED', _('Terminé')
        ABANDONED = 'ABANDONED', _('Abandonné')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name=_('Étudiant')
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Quiz')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    score = models.PositiveIntegerField(_('Score obtenu'), default=0)
    total_points = models.PositiveIntegerField(_('Total points'), default=0)
    percentage = models.FloatField(_('Pourcentage'), default=0)
    is_passed = models.BooleanField(_('Réussi'), default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Tentative de quiz')
        verbose_name_plural = _('Tentatives de quiz')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.quiz.title} ({self.percentage}%)"

    def calculate_score(self):
        """Calcule le score basé sur les réponses de l'utilisateur."""
        total_points = 0
        earned_points = 0

        for question in self.quiz.questions.all():
            total_points += question.points
            user_answers = self.user_answers.filter(question=question)

            if not user_answers.exists():
                continue

            correct_answer_ids = set(question.correct_answers.values_list('id', flat=True))
            user_answer_ids = set(user_answers.values_list('answer_id', flat=True))

            # Points attribués seulement si EXACTEMENT les bonnes réponses sont cochées
            if correct_answer_ids == user_answer_ids and correct_answer_ids:
                earned_points += question.points

        self.score = earned_points
        self.total_points = total_points
        self.percentage = round((earned_points / total_points) * 100, 1) if total_points > 0 else 0
        self.is_passed = self.percentage >= self.quiz.passing_score
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()


class UserAnswer(models.Model):
    """Réponse d'un utilisateur à une question."""

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name=_('Tentative')
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_('Question')
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        verbose_name=_('Réponse sélectionnée')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Réponse utilisateur')
        verbose_name_plural = _('Réponses utilisateurs')
        unique_together = [['attempt', 'question', 'answer']]

    def __str__(self):
        return f"{self.attempt.student} - Q{self.question.order}"