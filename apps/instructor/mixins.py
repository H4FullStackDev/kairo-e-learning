from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404


class InstructorRequiredMixin(LoginRequiredMixin):
    """
    Mixin qui vérifie que l'utilisateur est bien un formateur.
    Hérite de LoginRequiredMixin donc redirige vers login si non connecté.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Vérifier le rôle
        if not (request.user.is_instructor or request.user.is_superuser):
            messages.error(
                request,
                "Cet espace est réservé aux formateurs. Contactez l'administrateur pour devenir formateur."
            )
            return redirect('courses:course_list')

        return super().dispatch(request, *args, **kwargs)


class CourseOwnerMixin:
    """
    Mixin qui vérifie que le formateur est bien propriétaire du cours.
    Doit être combiné avec InstructorRequiredMixin.
    """

    def get_course(self):
        from apps.courses.models import Course
        course_id = self.kwargs.get('course_id') or self.kwargs.get('pk')
        course_slug = self.kwargs.get('course_slug')

        if course_slug:
            return get_object_or_404(Course, slug=course_slug)
        return get_object_or_404(Course, pk=course_id)

    def dispatch(self, request, *args, **kwargs):
        course = self.get_course()

        # Admin a tous les droits
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Vérifier que l'utilisateur est l'instructor du cours
        if course.instructor != request.user:
            messages.error(request, "Vous n'avez pas la permission de modifier ce cours.")
            return redirect('instructor:dashboard')

        return super().dispatch(request, *args, **kwargs)