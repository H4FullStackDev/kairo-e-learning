from django.apps import AppConfig


class CertificatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.certificates'
    label = 'certificates'
    verbose_name = 'Certificats'

    def ready(self):
        # Importer les signaux pour génération automatique
        from . import signals  # noqa