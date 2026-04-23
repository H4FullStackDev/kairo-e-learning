from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import ListView
from django.utils import timezone

from apps.courses.models import Lesson
from apps.enrollments.models import Enrollment
from .models import Comment, Notification


# ============================
# COMMENTAIRES
# ============================

@login_required
@require_POST
def post_comment(request, lesson_id):
    """Poste un nouveau commentaire ou une réponse."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # Vérifier que l'utilisateur a accès (inscrit OU formateur)
    is_instructor = request.user == lesson.chapter.course.instructor
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=lesson.chapter.course
    ).exists()

    if not is_enrolled and not is_instructor:
        messages.error(request, "Vous devez être inscrit pour commenter.")
        return redirect('courses:course_detail', slug=lesson.chapter.course.slug)

    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        messages.error(request, "Le commentaire ne peut pas être vide.")
        return redirect('enrollments:lesson_detail', course_slug=lesson.chapter.course.slug, lesson_id=lesson.id)

    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id, lesson=lesson)
        except Comment.DoesNotExist:
            pass

    Comment.objects.create(
        lesson=lesson,
        author=request.user,
        parent=parent,
        content=content,
    )

    messages.success(request, "Commentaire publié.")
    return redirect(f"{request.META.get('HTTP_REFERER', '/')}#comments")


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Supprime un commentaire (auteur uniquement)."""
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    comment.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def toggle_like_comment(request, comment_id):
    """Like/unlike un commentaire."""
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.liked_by.filter(pk=request.user.pk).exists():
        comment.liked_by.remove(request.user)
        liked = False
    else:
        comment.liked_by.add(request.user)
        liked = True

    return JsonResponse({
        'success': True,
        'liked': liked,
        'count': comment.likes_count,
    })


# ============================
# NOTIFICATIONS
# ============================

class NotificationsListView(LoginRequiredMixin, ListView):
    """Page complète des notifications."""
    template_name = 'interactions/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'related_course').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context


@login_required
@require_GET
def notifications_dropdown(request):
    """Retourne les 10 dernières notifications (pour le dropdown)."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'related_course').order_by('-created_at')[:10]

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    # Rendre le HTML directement
    html = render(request, 'interactions/partials/notif_dropdown_content.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    }).content.decode('utf-8')

    return JsonResponse({
        'html': html,
        'unread_count': unread_count,
    })


@login_required
@require_GET
def notifications_count(request):
    """Retourne juste le nombre de notifs non lues (pour polling léger)."""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    return JsonResponse({'count': count})


@login_required
def mark_notification_read(request, notif_id):
    """Marque une notification comme lue et redirige vers son target_url."""
    notification = get_object_or_404(Notification, pk=notif_id, recipient=request.user)
    notification.mark_as_read()

    if notification.target_url:
        return redirect(notification.target_url)
    return redirect('interactions:notifications_list')


@login_required
@require_POST
def mark_all_read(request):
    """Marque toutes les notifications comme lues."""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return JsonResponse({'success': True})