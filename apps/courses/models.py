from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Catégorie de cours (ex: Informatique, Marketing, Design...)."""

    name = models.CharField(_('Nom'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    icon = models.CharField(
        _('Icône (emoji ou classe)'),
        max_length=50,
        blank=True,
        help_text=_("Ex: 💻 ou nom d'une icône")
    )
    color = models.CharField(
        _('Couleur (hex)'),
        max_length=7,
        default='#6366F1',
        help_text=_('Couleur pour l\'affichage, ex: #6366F1')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:category_detail', kwargs={'slug': self.slug})

    @property
    def courses_count(self):
        return self.courses.filter(status=Course.Status.PUBLISHED).count()


class Course(models.Model):
    """Modèle principal d'un cours."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        PUBLISHED = 'PUBLISHED', _('Publié')
        ARCHIVED = 'ARCHIVED', _('Archivé')

    class Level(models.TextChoices):
        BEGINNER = 'BEGINNER', _('Débutant')
        INTERMEDIATE = 'INTERMEDIATE', _('Intermédiaire')
        ADVANCED = 'ADVANCED', _('Avancé')

    # Informations principales
    title = models.CharField(_('Titre'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True, blank=True)
    short_description = models.CharField(
        _('Description courte'),
        max_length=300,
        help_text=_('Résumé affiché dans les listings')
    )
    description = models.TextField(_('Description complète'))

    # Relations
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role__in': ['INSTRUCTOR', 'ADMIN']},
        verbose_name=_('Formateur')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        verbose_name=_('Catégorie')
    )

    # Média
    thumbnail = models.ImageField(
        _('Image de couverture'),
        upload_to='courses/thumbnails/',
        blank=True,
        null=True
    )
    trailer_video = models.FileField(
        _('Vidéo d\'introduction'),
        upload_to='courses/trailers/',
        blank=True,
        null=True,
        help_text=_('Vidéo de présentation (facultatif)')
    )

    # Paramètres
    level = models.CharField(
        _('Niveau'),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER
    )
    price = models.DecimalField(
        _('Prix (FCFA)'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('0 pour un cours gratuit')
    )
    duration_hours = models.PositiveIntegerField(
        _('Durée estimée (heures)'),
        default=0,
        help_text=_('Durée totale estimée en heures')
    )
    language = models.CharField(_('Langue'), max_length=50, default='Français')

    # Objectifs pédagogiques
    objectives = models.TextField(
        _('Objectifs pédagogiques'),
        blank=True,
        help_text=_('Un objectif par ligne')
    )
    prerequisites = models.TextField(
        _('Prérequis'),
        blank=True,
        help_text=_('Un prérequis par ligne')
    )

    # Statut
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    is_featured = models.BooleanField(_('Mis en avant'), default=False)

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Cours')
        verbose_name_plural = _('Cours')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})

    @property
    def is_free(self):
        return self.price == 0

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def total_lessons(self):
        """Nombre total de leçons dans ce cours."""
        return Lesson.objects.filter(chapter__course=self).count()

    @property
    def total_chapters(self):
        return self.chapters.count()

    def get_objectives_list(self):
        """Retourne les objectifs sous forme de liste."""
        return [obj.strip() for obj in self.objectives.split('\n') if obj.strip()]

    def get_prerequisites_list(self):
        return [pre.strip() for pre in self.prerequisites.split('\n') if pre.strip()]


class Chapter(models.Model):
    """Chapitre d'un cours (regroupe plusieurs leçons)."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name=_('Cours')
    )
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(_('Ordre'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Chapitre')
        verbose_name_plural = _('Chapitres')
        ordering = ['order', 'created_at']
        unique_together = [['course', 'order']]

    def __str__(self):
        return f"{self.course.title} - Chapitre {self.order}: {self.title}"

    @property
    def total_lessons(self):
        return self.lessons.count()


class Lesson(models.Model):
    """Leçon individuelle dans un chapitre."""

    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', _('Vidéo')
        PDF = 'PDF', _('PDF')
        TEXT = 'TEXT', _('Texte')
        MIXED = 'MIXED', _('Contenu mixte')

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('Chapitre')
    )
    title = models.CharField(_('Titre'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=220, blank=True)
    content_type = models.CharField(
        _('Type de contenu'),
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.VIDEO
    )

    # Contenus
    video = models.FileField(
        _('Fichier vidéo'),
        upload_to='lessons/videos/',
        blank=True,
        null=True
    )
    video_url = models.URLField(
        _('URL vidéo externe'),
        blank=True,
        help_text=_('Lien YouTube, Vimeo, etc. (alternative au fichier)')
    )
    pdf_file = models.FileField(
        _('Fichier PDF'),
        upload_to='lessons/pdfs/',
        blank=True,
        null=True
    )
    text_content = models.TextField(_('Contenu texte'), blank=True)

    # Paramètres
    order = models.PositiveIntegerField(_('Ordre'), default=0)
    duration_minutes = models.PositiveIntegerField(
        _('Durée (minutes)'),
        default=0,
        help_text=_('Durée estimée de la leçon en minutes')
    )
    is_free_preview = models.BooleanField(
        _('Aperçu gratuit'),
        default=False,
        help_text=_('Accessible sans inscription')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Leçon')
        verbose_name_plural = _('Leçons')
        ordering = ['chapter', 'order']
        unique_together = [['chapter', 'order']]

    def __str__(self):
        return f"{self.chapter.title} - Leçon {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def course(self):
        return self.chapter.course