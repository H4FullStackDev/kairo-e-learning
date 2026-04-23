from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Lesson, Course


class Comment(models.Model):
    """Commentaire sous une leçon, avec réponses imbriquées."""

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Leçon')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Auteur')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name=_('Commentaire parent')
    )

    content = models.TextField(_('Contenu'))

    # Likes / utilité
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True,
        verbose_name=_('Utilisateurs ayant aimé')
    )

    is_instructor_reply = models.BooleanField(
        _('Réponse du formateur'),
        default=False,
        help_text=_('True si l\'auteur est le formateur du cours')
    )
    is_pinned = models.BooleanField(_('Épinglé'), default=False)
    is_edited = models.BooleanField(_('Édité'), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Commentaire')
        verbose_name_plural = _('Commentaires')
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['lesson', '-created_at']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        prefix = "↳ " if self.parent else ""
        return f"{prefix}{self.author.get_full_name()}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        # Marquer automatiquement si l'auteur est le formateur du cours
        if not self.pk:
            if self.author == self.lesson.chapter.course.instructor:
                self.is_instructor_reply = True
        super().save(*args, **kwargs)

    @property
    def likes_count(self):
        return self.liked_by.count()

    @property
    def replies_count(self):
        return self.replies.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.liked_by.filter(pk=user.pk).exists()


class Notification(models.Model):
    """Notification pour un utilisateur."""

    class Type(models.TextChoices):
        COMMENT_REPLY = 'COMMENT_REPLY', _('Réponse à votre commentaire')
        INSTRUCTOR_REPLY = 'INSTRUCTOR_REPLY', _('Le formateur a répondu')
        COMMENT_LIKED = 'COMMENT_LIKED', _('Votre commentaire a été aimé')
        COURSE_COMPLETED = 'COURSE_COMPLETED', _('Cours terminé')
        CERTIFICATE_READY = 'CERTIFICATE_READY', _('Certificat disponible')
        QUIZ_PASSED = 'QUIZ_PASSED', _('Quiz réussi')
        NEW_LESSON = 'NEW_LESSON', _('Nouvelle leçon disponible')
        ENROLLMENT = 'ENROLLMENT', _('Nouvelle inscription à votre cours')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Destinataire')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True,
        verbose_name=_('Émetteur')
    )

    notification_type = models.CharField(
        _('Type'),
        max_length=30,
        choices=Type.choices
    )
    title = models.CharField(_('Titre'), max_length=200)
    message = models.TextField(_('Message'), blank=True)

    # Cible (URL à atteindre en cliquant)
    target_url = models.CharField(_('URL cible'), max_length=500, blank=True)

    # Métadonnées pour contexte
    related_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    is_read = models.BooleanField(_('Lu'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.recipient} ← {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def get_icon_name(self):
        """Retourne le nom de l'icône à utiliser."""
        icon_map = {
            self.Type.COMMENT_REPLY: 'mail',
            self.Type.INSTRUCTOR_REPLY: 'graduation-cap',
            self.Type.COMMENT_LIKED: 'star',
            self.Type.COURSE_COMPLETED: 'check',
            self.Type.CERTIFICATE_READY: 'award',
            self.Type.QUIZ_PASSED: 'check',
            self.Type.NEW_LESSON: 'video',
            self.Type.ENROLLMENT: 'users',
        }
        return icon_map.get(self.notification_type, 'sparkles')