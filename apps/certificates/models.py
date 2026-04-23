import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Course
from apps.enrollments.models import Enrollment


def generate_certificate_number():
    """Génère un numéro unique : KRS-2026-XXXXXXXX"""
    from django.utils import timezone
    year = timezone.now().year
    unique = uuid.uuid4().hex[:8].upper()
    return f"KRS-{year}-{unique}"


class Certificate(models.Model):
    """Certificat de réussite d'un cours."""

    # Identifiants uniques
    certificate_number = models.CharField(
        _('Numéro de certificat'),
        max_length=30,
        unique=True,
        default=generate_certificate_number,
        help_text=_('Identifiant unique du certificat')
    )
    verification_uuid = models.UUIDField(
        _('UUID de vérification'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # Relations
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_('Étudiant')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_('Cours')
    )
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name=_('Inscription')
    )

    # Informations
    student_name = models.CharField(
        _('Nom de l\'étudiant (figé)'),
        max_length=200,
        help_text=_('Nom au moment de la génération')
    )
    course_title = models.CharField(
        _('Titre du cours (figé)'),
        max_length=200,
        help_text=_('Titre du cours au moment de la génération')
    )
    instructor_name = models.CharField(
        _('Nom du formateur (figé)'),
        max_length=200
    )
    completion_percentage = models.PositiveIntegerField(
        _('% de complétion'),
        default=100
    )
    quiz_score = models.FloatField(
        _('Score du quiz final (%)'),
        null=True,
        blank=True
    )

    # Fichier PDF généré
    pdf_file = models.FileField(
        _('Fichier PDF'),
        upload_to='certificates/',
        null=True,
        blank=True
    )

    # Dates
    issued_at = models.DateTimeField(_('Délivré le'), auto_now_add=True)
    course_completed_at = models.DateTimeField(
        _('Cours terminé le'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Certificat')
        verbose_name_plural = _('Certificats')
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['certificate_number']),
            models.Index(fields=['verification_uuid']),
        ]

    def __str__(self):
        return f"{self.certificate_number} — {self.student_name}"

    def get_absolute_url(self):
        return reverse('certificates:detail', kwargs={'uuid': self.verification_uuid})

    def get_verification_url(self):
        return reverse('certificates:verify', kwargs={'uuid': self.verification_uuid})

    def generate_pdf(self):
        """Génère le PDF du certificat et l'enregistre."""
        from .pdf_generator import create_certificate_pdf
        from django.core.files.base import ContentFile

        pdf_bytes = create_certificate_pdf(self)
        filename = f"{self.certificate_number}.pdf"
        self.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
        return self.pdf_file