from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.courses.models import Course, Lesson


class Enrollment(models.Model):
    """Inscription d'un étudiant à un cours."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('En cours')
        COMPLETED = 'COMPLETED', _('Terminé')
        CANCELLED = 'CANCELLED', _('Annulé')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Étudiant')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Cours')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    enrolled_at = models.DateTimeField(_('Inscrit le'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Terminé le'), null=True, blank=True)
    last_accessed_at = models.DateTimeField(_('Dernier accès'), auto_now=True)

    class Meta:
        verbose_name = _('Inscription')
        verbose_name_plural = _('Inscriptions')
        unique_together = [['student', 'course']]
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.course.title}"

    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression."""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0
        completed = LessonProgress.objects.filter(
            enrollment=self,
            is_completed=True
        ).count()
        return round((completed / total_lessons) * 100)

    @property
    def completed_lessons_count(self):
        return LessonProgress.objects.filter(enrollment=self, is_completed=True).count()

    @property
    def total_lessons_count(self):
        return self.course.total_lessons

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    def get_next_lesson(self):
        """Retourne la prochaine leçon non terminée."""
        completed_lesson_ids = LessonProgress.objects.filter(
            enrollment=self,
            is_completed=True
        ).values_list('lesson_id', flat=True)

        next_lesson = Lesson.objects.filter(
            chapter__course=self.course
        ).exclude(
            id__in=completed_lesson_ids
        ).order_by('chapter__order', 'order').first()

        return next_lesson

    def mark_as_completed_if_done(self):
        """Marque l'inscription comme terminée si toutes les leçons sont faites."""
        if self.progress_percentage == 100 and self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save()
            return True
        return False


class LessonProgress(models.Model):
    """Progression d'un étudiant sur une leçon spécifique."""

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name=_('Inscription')
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('Leçon')
    )
    is_completed = models.BooleanField(_('Terminée'), default=False)
    completed_at = models.DateTimeField(_('Terminée le'), null=True, blank=True)
    last_position_seconds = models.PositiveIntegerField(
        _('Dernière position (secondes)'),
        default=0,
        help_text=_('Position de lecture pour les vidéos')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Progression de leçon')
        verbose_name_plural = _('Progressions de leçons')
        unique_together = [['enrollment', 'lesson']]
        ordering = ['-updated_at']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.enrollment.student.get_full_name()} - {self.lesson.title}"

    def mark_completed(self):
        """Marque la leçon comme terminée."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            # Vérifier si le cours est terminé
            self.enrollment.mark_as_completed_if_done()

    def mark_uncompleted(self):
        """Remet la leçon en "non terminée"."""
        self.is_completed = False
        self.completed_at = None
        self.save()
        if self.enrollment.status == Enrollment.Status.COMPLETED:
            self.enrollment.status = Enrollment.Status.ACTIVE
            self.enrollment.completed_at = None
            self.enrollment.save()