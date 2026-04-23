from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec gestion des rôles.
    Hérite de AbstractUser pour garder les fonctionnalités de base de Django.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        INSTRUCTOR = 'INSTRUCTOR', _('Formateur')
        STUDENT = 'STUDENT', _('Étudiant')

    # Email obligatoire et unique (pour la connexion)
    email = models.EmailField(_('Adresse email'), unique=True)

    # Rôle de l'utilisateur
    role = models.CharField(
        _('Rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Champs supplémentaires pour le profil
    bio = models.TextField(_('Biographie'), blank=True, null=True)
    avatar = models.ImageField(
        _('Photo de profil'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    phone = models.CharField(_('Téléphone'), max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(_('Date de naissance'), blank=True, null=True)

    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Mis à jour le'), auto_now=True)

    # Utiliser l'email comme identifiant de connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    def get_full_name(self):
        """Retourne le nom complet ou l'email si vide."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email