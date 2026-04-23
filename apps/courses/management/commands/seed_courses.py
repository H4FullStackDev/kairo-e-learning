from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import Category, Course, Chapter, Lesson
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Génère des données de démonstration pour les cours'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🌱 Génération des données de démo...'))

        # On utilise des noms d'icônes SVG (mappés dans le template partial)
        categories_data = [
            {'name': 'Intelligence Artificielle', 'icon': 'brain', 'color': '#D97706', 'description': 'Machine Learning, Deep Learning, NLP, Computer Vision.'},
            {'name': 'Développement Web', 'icon': 'code', 'color': '#1E40AF', 'description': 'Frontend, Backend, Full-stack avec les frameworks modernes.'},
            {'name': 'Data Science', 'icon': 'chart', 'color': '#166534', 'description': 'Analyse de données, statistiques, visualisation.'},
            {'name': 'Design & UX', 'icon': 'palette', 'color': '#7C3AED', 'description': 'UI/UX Design, Figma, principes de design moderne.'},
            {'name': 'Marketing Digital', 'icon': 'megaphone', 'color': '#BE185D', 'description': 'SEO, Social Media, Growth Hacking, Analytics.'},
            {'name': 'Business & Management', 'icon': 'briefcase', 'color': '#0F766E', 'description': 'Entrepreneuriat, gestion de projet, leadership.'},
        ]

        for cat_data in categories_data:
            cat, _ = Category.objects.update_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            self.stdout.write(f'  ✓ Catégorie : {cat.name}')

        # --- Formateur de démo ---
        instructor, created = User.objects.get_or_create(
            username='formateur_demo',
            defaults={
                'email': 'formateur@kairos.tg',
                'first_name': 'Marie',
                'last_name': 'Kodjo',
                'role': User.Role.INSTRUCTOR,
                'bio': 'Experte en IA avec plus de 10 ans d\'expérience dans l\'industrie.',
            }
        )
        if created:
            instructor.set_password('demo12345')
            instructor.save()
            self.stdout.write(f'  ✓ Formateur créé : {instructor.email} (mdp: demo12345)')

        courses_data = [
            {
                'title': 'Introduction au Machine Learning',
                'short_description': 'Découvrez les fondamentaux du Machine Learning avec Python et scikit-learn.',
                'description': 'Un parcours complet pour maîtriser les bases du Machine Learning. De la régression linéaire aux réseaux de neurones, apprenez avec des projets concrets et des cas d\'usage réels.',
                'category': 'Intelligence Artificielle',
                'level': 'BEGINNER', 'price': 0, 'duration_hours': 12,
                'objectives': 'Comprendre les algorithmes de ML\nManipuler scikit-learn\nRéaliser un projet complet\nÉvaluer un modèle',
                'prerequisites': 'Python de base\nMathématiques niveau lycée',
                'is_featured': True, 'status': 'PUBLISHED',
            },
            {
                'title': 'Deep Learning avec PyTorch',
                'short_description': 'Maîtrisez les réseaux de neurones modernes avec PyTorch.',
                'description': 'Plongez dans le Deep Learning avec l\'un des frameworks les plus utilisés. CNN, RNN, Transformers — tous les concepts clés expliqués avec des projets pratiques.',
                'category': 'Intelligence Artificielle',
                'level': 'ADVANCED', 'price': 25000, 'duration_hours': 30,
                'objectives': 'Construire des CNN\nEntraîner des RNN\nUtiliser les Transformers\nDéployer un modèle',
                'prerequisites': 'Machine Learning de base\nPython avancé',
                'is_featured': True, 'status': 'PUBLISHED',
            },
            {
                'title': 'Django pour les débutants',
                'short_description': 'Construisez votre première application web avec Django.',
                'description': 'Apprenez Django de A à Z. De l\'installation au déploiement, construisez une vraie application web moderne.',
                'category': 'Développement Web',
                'level': 'BEGINNER', 'price': 15000, 'duration_hours': 20,
                'objectives': 'Maîtriser le pattern MVT\nCréer des modèles\nGérer l\'authentification\nDéployer sur un serveur',
                'prerequisites': 'Python de base\nHTML/CSS',
                'status': 'PUBLISHED',
            },
            {
                'title': 'React & Next.js 14',
                'short_description': 'Le guide complet pour devenir développeur React moderne.',
                'description': 'Maîtrisez React et Next.js 14. Server Components, App Router, tout ce qu\'il faut pour construire des apps modernes.',
                'category': 'Développement Web',
                'level': 'INTERMEDIATE', 'price': 20000, 'duration_hours': 25,
                'is_featured': True, 'status': 'PUBLISHED',
            },
            {
                'title': 'Analyse de données avec Pandas',
                'short_description': 'L\'outil incontournable pour manipuler des données en Python.',
                'description': 'Maîtrisez Pandas, la bibliothèque de référence pour l\'analyse de données. Nettoyage, transformation, visualisation.',
                'category': 'Data Science',
                'level': 'BEGINNER', 'price': 0, 'duration_hours': 15,
                'status': 'PUBLISHED',
            },
            {
                'title': 'UX Design : Les fondamentaux',
                'short_description': 'Concevez des interfaces centrées utilisateur.',
                'description': 'Apprenez les principes du UX Design moderne. Wireframing, prototypage, tests utilisateurs.',
                'category': 'Design & UX',
                'level': 'BEGINNER', 'price': 18000, 'duration_hours': 18,
                'status': 'PUBLISHED',
            },
            {
                'title': 'SEO avancé en 2026',
                'short_description': 'Dominez les moteurs de recherche avec les techniques modernes.',
                'description': 'Les dernières techniques SEO qui fonctionnent vraiment en 2026. Core Web Vitals, IA, contenu optimisé.',
                'category': 'Marketing Digital',
                'level': 'INTERMEDIATE', 'price': 22000, 'duration_hours': 16,
                'status': 'PUBLISHED',
            },
            {
                'title': 'Entrepreneuriat tech en Afrique',
                'short_description': 'Lancez votre startup tech sur le continent africain.',
                'description': 'De l\'idée au premier million. Tout ce qu\'il faut savoir pour créer une startup tech en Afrique.',
                'category': 'Business & Management',
                'level': 'INTERMEDIATE', 'price': 30000, 'duration_hours': 22,
                'is_featured': True, 'status': 'PUBLISHED',
            },
        ]

        for course_data in courses_data:
            cat_name = course_data.pop('category')
            category = Category.objects.get(name=cat_name)

            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={**course_data, 'instructor': instructor, 'category': category}
            )

            if created:
                self.stdout.write(f'  ✓ Cours créé : {course.title}')
                for i in range(1, 4):
                    chapter = Chapter.objects.create(
                        course=course,
                        title=f'Chapitre {i}',
                        description=f'Description du chapitre {i}',
                        order=i
                    )
                    for j in range(1, 4):
                        Lesson.objects.create(
                            chapter=chapter,
                            title=f'Leçon {j} du chapitre {i}',
                            content_type='VIDEO',
                            order=j,
                            duration_minutes=random.randint(10, 30),
                            is_free_preview=(i == 1 and j == 1),
                        )

        self.stdout.write(self.style.SUCCESS('\n✅ Génération terminée !'))