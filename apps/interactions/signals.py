from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse

from apps.enrollments.models import Enrollment
from apps.certificates.models import Certificate
from apps.quizzes.models import QuizAttempt
from .models import Comment, Notification


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    """Crée des notifications pour les réponses et les mentions."""
    if not created:
        return

    lesson_url = reverse('enrollments:lesson_detail', kwargs={
        'course_slug': instance.lesson.chapter.course.slug,
        'lesson_id': instance.lesson.id
    }) + f'#comment-{instance.id}'

    # 1. Si c'est une réponse → notifier le parent
    if instance.parent and instance.parent.author != instance.author:
        notif_type = (
            Notification.Type.INSTRUCTOR_REPLY
            if instance.is_instructor_reply
            else Notification.Type.COMMENT_REPLY
        )

        title = (
            f"{instance.author.get_full_name()} (formateur) a répondu à votre commentaire"
            if instance.is_instructor_reply
            else f"{instance.author.get_full_name()} a répondu à votre commentaire"
        )

        Notification.objects.create(
            recipient=instance.parent.author,
            sender=instance.author,
            notification_type=notif_type,
            title=title,
            message=instance.content[:150],
            target_url=lesson_url,
            related_course=instance.lesson.chapter.course,
            related_comment=instance,
        )

    # 2. Si c'est un commentaire racine posé par un étudiant → notifier le formateur
    elif not instance.parent and not instance.is_instructor_reply:
        instructor = instance.lesson.chapter.course.instructor
        if instructor != instance.author:
            Notification.objects.create(
                recipient=instructor,
                sender=instance.author,
                notification_type=Notification.Type.COMMENT_REPLY,
                title=f"Nouveau commentaire de {instance.author.get_full_name()}",
                message=instance.content[:150],
                target_url=lesson_url,
                related_course=instance.lesson.chapter.course,
                related_comment=instance,
            )


@receiver(m2m_changed, sender=Comment.liked_by.through)
def notify_on_like(sender, instance, action, pk_set, **kwargs):
    """Notifie l'auteur quand son commentaire est aimé."""
    if action == 'post_add' and pk_set:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        for user_id in pk_set:
            try:
                liker = User.objects.get(pk=user_id)
                if liker != instance.author:
                    # Éviter de spammer : ne créer qu'une notif si pas déjà une récente
                    recent_exists = Notification.objects.filter(
                        recipient=instance.author,
                        sender=liker,
                        related_comment=instance,
                        notification_type=Notification.Type.COMMENT_LIKED,
                    ).exists()

                    if not recent_exists:
                        lesson_url = reverse('enrollments:lesson_detail', kwargs={
                            'course_slug': instance.lesson.chapter.course.slug,
                            'lesson_id': instance.lesson.id
                        }) + f'#comment-{instance.id}'

                        Notification.objects.create(
                            recipient=instance.author,
                            sender=liker,
                            notification_type=Notification.Type.COMMENT_LIKED,
                            title=f"{liker.get_full_name()} a trouvé votre commentaire utile",
                            message=instance.content[:100],
                            target_url=lesson_url,
                            related_course=instance.lesson.chapter.course,
                            related_comment=instance,
                        )
            except User.DoesNotExist:
                continue


@receiver(post_save, sender=Enrollment)
def notify_on_enrollment(sender, instance, created, **kwargs):
    """Notifie le formateur d'une nouvelle inscription + notifie l'étudiant si cours terminé."""
    if created:
        # Notification pour le formateur
        instructor = instance.course.instructor
        if instructor != instance.student:
            Notification.objects.create(
                recipient=instructor,
                sender=instance.student,
                notification_type=Notification.Type.ENROLLMENT,
                title=f"Nouvelle inscription : {instance.student.get_full_name()}",
                message=f"S'est inscrit(e) à « {instance.course.title} »",
                target_url=reverse('courses:course_detail', kwargs={'slug': instance.course.slug}),
                related_course=instance.course,
            )

    # Notification étudiant quand cours terminé
    if instance.status == Enrollment.Status.COMPLETED:
        recent_exists = Notification.objects.filter(
            recipient=instance.student,
            related_course=instance.course,
            notification_type=Notification.Type.COURSE_COMPLETED,
        ).exists()

        if not recent_exists:
            Notification.objects.create(
                recipient=instance.student,
                notification_type=Notification.Type.COURSE_COMPLETED,
                title=f"🎉 Vous avez terminé le cours !",
                message=f"Félicitations pour avoir complété « {instance.course.title} »",
                target_url=reverse('enrollments:my_courses'),
                related_course=instance.course,
            )


@receiver(post_save, sender=Certificate)
def notify_certificate_ready(sender, instance, created, **kwargs):
    """Notifie l'étudiant quand son certificat est prêt."""
    if created:
        Notification.objects.create(
            recipient=instance.student,
            notification_type=Notification.Type.CERTIFICATE_READY,
            title="🏆 Votre certificat est prêt !",
            message=f"Téléchargez votre certificat pour « {instance.course_title} »",
            target_url=reverse('certificates:detail', kwargs={'uuid': instance.verification_uuid}),
            related_course=instance.course,
        )


@receiver(post_save, sender=QuizAttempt)
def notify_quiz_passed(sender, instance, created, **kwargs):
    """Notifie quand un quiz est réussi."""
    if instance.status == QuizAttempt.Status.COMPLETED and instance.is_passed:
        recent_exists = Notification.objects.filter(
            recipient=instance.student,
            notification_type=Notification.Type.QUIZ_PASSED,
            related_course=instance.quiz.course,
        ).filter(created_at__date=instance.completed_at.date()).exists()

        if not recent_exists:
            Notification.objects.create(
                recipient=instance.student,
                notification_type=Notification.Type.QUIZ_PASSED,
                title=f"Quiz réussi avec {instance.percentage:.0f}% !",
                message=f"« {instance.quiz.title} »",
                target_url=reverse('quizzes:quiz_result', kwargs={'attempt_id': instance.id}),
                related_course=instance.quiz.course,
            )