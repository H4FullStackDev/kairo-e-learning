from django import template

register = template.Library()


@register.filter(name='is_liked_by')
def is_liked_by(comment, user):
    """Vérifie si un commentaire est aimé par l'utilisateur."""
    if not user.is_authenticated:
        return False
    return comment.liked_by.filter(pk=user.pk).exists()