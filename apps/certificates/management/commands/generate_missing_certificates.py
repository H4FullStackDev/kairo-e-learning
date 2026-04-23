from django.core.management.base import BaseCommand
from apps.enrollments.models import Enrollment
from apps.certificates.models import Certificate
from apps.quizzes.models import Quiz, QuizAttempt


class Command(BaseCommand):
    help = 'Génère les certificats manquants pour les cours déjà terminés'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🏆 Génération des certificats manquants...\n'))

        completed_enrollments = Enrollment.objects.filter(
            status=Enrollment.Status.COMPLETED
        )

        created_count = 0
        for enrollment in completed_enrollments:
            # Vérifier s'il existe déjà un certificat
            if Certificate.objects.filter(enrollment=enrollment).exists():
                continue

            # Récupérer le meilleur score de quiz
            best_score = None
            final_quiz = Quiz.objects.filter(
                course=enrollment.course,
                quiz_type=Quiz.QuizType.COURSE_FINAL,
                is_active=True
            ).first()

            if final_quiz:
                best_attempt = QuizAttempt.objects.filter(
                    student=enrollment.student,
                    quiz=final_quiz,
                    is_passed=True
                ).order_by('-percentage').first()

                if best_attempt:
                    best_score = best_attempt.percentage

            # Créer le certificat
            certificate = Certificate.objects.create(
                student=enrollment.student,
                course=enrollment.course,
                enrollment=enrollment,
                student_name=enrollment.student.get_full_name() or enrollment.student.username,
                course_title=enrollment.course.title,
                instructor_name=enrollment.course.instructor.get_full_name() or enrollment.course.instructor.username,
                completion_percentage=100,
                quiz_score=best_score,
                course_completed_at=enrollment.completed_at,
            )

            try:
                certificate.generate_pdf()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Certificat créé : {certificate.certificate_number} pour {enrollment.student.email}'))
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Erreur pour {enrollment.student.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {created_count} certificats créés !\n'))