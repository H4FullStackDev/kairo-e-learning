from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Sum
from django.views.generic import ListView, DetailView
from .models import Course, Category, Chapter, Lesson


class CourseListView(ListView):
    """Liste publique des cours avec filtres."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('instructor', 'category')

        # Filtre par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filtre par niveau
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)

        # Filtre prix (gratuit/payant)
        price_filter = self.request.GET.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(price=0)
        elif price_filter == 'paid':
            queryset = queryset.filter(price__gt=0)

        # Recherche
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(description__icontains=search)
            )

        # Tri
        sort = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['-created_at', 'created_at', 'price', '-price', 'title']
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            published_count=Count('courses', filter=Q(courses__status=Course.Status.PUBLISHED))
        ).filter(published_count__gt=0)
        context['levels'] = Course.Level.choices
        context['current_category'] = self.request.GET.get('category', '')
        context['current_level'] = self.request.GET.get('level', '')
        context['current_price'] = self.request.GET.get('price', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['current_search'] = self.request.GET.get('q', '')
        context['total_courses'] = Course.objects.filter(status=Course.Status.PUBLISHED).count()
        return context


class CourseDetailView(DetailView):
    """Page détail d'un cours."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Course.objects.filter(status=Course.Status.PUBLISHED).select_related('instructor', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['chapters'] = course.chapters.prefetch_related('lessons').order_by('order')
        context['total_lessons'] = course.total_lessons
        context['total_duration'] = sum(
            lesson.duration_minutes
            for chapter in context['chapters']
            for lesson in chapter.lessons.all()
        )
        context['related_courses'] = Course.objects.filter(
            category=course.category,
            status=Course.Status.PUBLISHED
        ).exclude(pk=course.pk)[:3]

        # NOUVEAU : Inscription de l'utilisateur courant
        if self.request.user.is_authenticated:
            from apps.enrollments.models import Enrollment
            context['user_enrollment'] = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).first()
        else:
            context['user_enrollment'] = None

        return context

class CategoryDetailView(DetailView):
    """Page d'une catégorie avec ses cours."""
    model = Category
    template_name = 'courses/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.courses.filter(
            status=Course.Status.PUBLISHED
        ).select_related('instructor')
        context['all_categories'] = Category.objects.all()
        return context