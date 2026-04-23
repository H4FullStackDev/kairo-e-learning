from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollments.models import Enrollment
from .models import Certificate


@receiver(post_save, sender=Enrollment)
def generate_certificate_on_completion(sender, instance, created, **kwargs):
    """
    Génère automatiquement un certificat quand un cours est terminé.
    """
    if instance.status == Enrollment.Status.COMPLETED:
        # Vérifier qu'il n'existe pas déjà un certificat
        if hasattr(instance, 'certificate'):
            return

        # Récupérer le meilleur score au quiz (s'il existe)
        from apps.quizzes.models import QuizAttempt, Quiz
        best_score = None
        final_quiz = Quiz.objects.filter(
            course=instance.course,
            quiz_type=Quiz.QuizType.COURSE_FINAL,
            is_active=True
        ).first()

        if final_quiz:
            best_attempt = QuizAttempt.objects.filter(
                student=instance.student,
                quiz=final_quiz,
                is_passed=True
            ).order_by('-percentage').first()

            if best_attempt:
                best_score = best_attempt.percentage

        # Créer le certificat
        certificate = Certificate.objects.create(
            student=instance.student,
            course=instance.course,
            enrollment=instance,
            student_name=instance.student.get_full_name() or instance.student.username,
            course_title=instance.course.title,
            instructor_name=instance.course.instructor.get_full_name() or instance.course.instructor.username,
            completion_percentage=100,
            quiz_score=best_score,
            course_completed_at=instance.completed_at,
        )

        # Générer le PDF
        try:
            certificate.generate_pdf()
        except Exception as e:
            print(f"Erreur lors de la génération du PDF : {e}")