from django.apps import AppConfig


class InstructorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.instructor'
    label = 'instructor'
    verbose_name = 'Espace Formateur'