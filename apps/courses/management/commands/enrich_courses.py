from django.core.management.base import BaseCommand
from apps.courses.models import Course, Chapter, Lesson


class Command(BaseCommand):
    help = 'Enrichit les cours existants avec du contenu vidéo et texte réel'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🎬 Enrichissement des cours avec du contenu réel...\n'))

        # Mapping cours → contenu enrichi
        # On utilise des vidéos YouTube éducatives populaires (FreeCodeCamp, etc.)
        enriched_data = {
            'Introduction au Machine Learning': {
                'thumbnail_color': '#D97706',
                'chapters': [
                    {
                        'title': 'Les fondamentaux du Machine Learning',
                        'description': 'Comprendre ce qu\'est le ML, ses types et ses applications.',
                        'lessons': [
                            {
                                'title': 'Qu\'est-ce que le Machine Learning ?',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/ukzFI9rgwfU',
                                'duration': 15,
                                'text_content': '''Le Machine Learning (ML) est une branche de l'intelligence artificielle qui permet aux ordinateurs d'apprendre à partir de données, sans être explicitement programmés pour chaque tâche.

Les 3 grandes familles de ML :

1. **Apprentissage supervisé** : l'algorithme apprend à partir de données étiquetées (ex: classification d'emails spam/non-spam).

2. **Apprentissage non-supervisé** : l'algorithme découvre lui-même des patterns dans des données non étiquetées (ex: segmentation de clientèle).

3. **Apprentissage par renforcement** : l'algorithme apprend par essai-erreur avec un système de récompenses (ex: AlphaGo).

Dans cette leçon, nous verrons les cas d'usage concrets et pourquoi le ML est au cœur de nombreuses applications modernes (Netflix, Spotify, voitures autonomes, etc.).''',
                                'is_free_preview': True,
                            },
                            {
                                'title': 'Types d\'apprentissage : supervisé vs non-supervisé',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/1FZ0A1QCMWc',
                                'duration': 20,
                                'text_content': 'Exploration approfondie des différences entre apprentissage supervisé et non-supervisé, avec des exemples concrets en Python.',
                            },
                            {
                                'title': 'Vue d\'ensemble de scikit-learn',
                                'content_type': 'TEXT',
                                'duration': 10,
                                'text_content': '''Scikit-learn est la bibliothèque Python de référence pour le Machine Learning classique.

**Installation :**
pip install scikit-learn

**Les modules principaux :**

- sklearn.datasets : jeux de données d'exemple (iris, digits, etc.)
- sklearn.model_selection : division train/test, validation croisée
- sklearn.preprocessing : normalisation, encodage
- sklearn.linear_model : régression linéaire, logistique
- sklearn.tree : arbres de décision
- sklearn.ensemble : Random Forest, Gradient Boosting
- sklearn.neighbors : k-NN
- sklearn.cluster : K-Means, DBSCAN
- sklearn.metrics : évaluation des modèles

**Le workflow type :**

1. Charger les données
2. Séparer en train/test
3. Choisir et instancier un modèle
4. L'entraîner avec .fit()
5. Prédire avec .predict()
6. Évaluer avec .score() ou d'autres métriques

Dans la prochaine leçon, nous coderons notre premier modèle ensemble.''',
                            },
                        ]
                    },
                    {
                        'title': 'Premiers pas avec scikit-learn',
                        'description': 'Construire votre premier modèle de prédiction.',
                        'lessons': [
                            {
                                'title': 'Installation et configuration de l\'environnement',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/WFr2WgN9_xE',
                                'duration': 12,
                                'text_content': 'Installation de Python, Jupyter, et des bibliothèques nécessaires pour le ML.',
                            },
                            {
                                'title': 'Votre premier modèle : régression linéaire',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/nk2CQITm_eo',
                                'duration': 25,
                                'text_content': '''La régression linéaire est le point de départ idéal pour comprendre le ML.

**Concept :** trouver la meilleure droite qui passe à travers un nuage de points.

**Formule :** y = ax + b

où :
- y = valeur à prédire
- x = variable d'entrée
- a = pente (coefficient)
- b = ordonnée à l'origine

**Exemple en Python :**

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)''',
                            },
                            {
                                'title': 'Évaluation et métriques de performance',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/7KAbqJZx-f8',
                                'duration': 18,
                            },
                        ]
                    },
                    {
                        'title': 'Projet pratique : prédire des prix immobiliers',
                        'description': 'Un projet complet de A à Z.',
                        'lessons': [
                            {
                                'title': 'Exploration et visualisation des données',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/eMOA1pPVUc4',
                                'duration': 22,
                            },
                            {
                                'title': 'Feature engineering et preprocessing',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/GduT2ZCc26E',
                                'duration': 28,
                            },
                            {
                                'title': 'Entraînement et optimisation du modèle',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/ZiKMIuYidY0',
                                'duration': 30,
                            },
                        ]
                    }
                ]
            },

            'Django pour les débutants': {
                'chapters': [
                    {
                        'title': 'Découverte de Django',
                        'description': 'Premiers pas avec le framework.',
                        'lessons': [
                            {
                                'title': 'Introduction à Django et installation',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/F5mRW0jo-U4',
                                'duration': 20,
                                'text_content': '''Django est un framework web Python haut niveau qui encourage un développement rapide et un design pragmatique.

**Pourquoi Django ?**

- Batteries incluses : ORM, admin, authentification, formulaires, sécurité
- Documentation exemplaire
- Scalable (Instagram, Pinterest, Disqus l'utilisent)
- Très productif : on peut faire beaucoup en peu de code

**Installation :**

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate  # Windows
pip install django

**Créer un projet :**

django-admin startproject monprojet .
python manage.py runserver''',
                                'is_free_preview': True,
                            },
                            {
                                'title': 'Architecture MVT (Model-View-Template)',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/HyJZLQYbAtE',
                                'duration': 18,
                            },
                            {
                                'title': 'Votre premier projet Django',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/rHux0gMZ3Eg',
                                'duration': 30,
                            },
                        ]
                    },
                    {
                        'title': 'Modèles et base de données',
                        'description': 'Maîtriser l\'ORM de Django.',
                        'lessons': [
                            {
                                'title': 'Définir vos premiers modèles',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/ACzY_lEB8Fc',
                                'duration': 22,
                            },
                            {
                                'title': 'Migrations et Django Admin',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/EyVHMa8pK1Y',
                                'duration': 15,
                            },
                            {
                                'title': 'Relations entre modèles (ForeignKey, ManyToMany)',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/w2xR4s1HM2o',
                                'duration': 25,
                            },
                        ]
                    },
                    {
                        'title': 'Vues, URLs et Templates',
                        'description': 'Construire l\'interface utilisateur.',
                        'lessons': [
                            {
                                'title': 'Vues basées sur des fonctions',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/NQLM0Uh7ihE',
                                'duration': 20,
                            },
                            {
                                'title': 'Templates Django et héritage',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/vF9n4TqZ0zI',
                                'duration': 18,
                            },
                            {
                                'title': 'Formulaires et validation',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/UmljXZIypDc',
                                'duration': 25,
                            },
                        ]
                    }
                ]
            },

            'React & Next.js 14': {
                'chapters': [
                    {
                        'title': 'Les bases de React',
                        'description': 'Composants, props, state.',
                        'lessons': [
                            {
                                'title': 'Introduction à React et JSX',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/SqcY0GlETPk',
                                'duration': 25,
                                'is_free_preview': True,
                            },
                            {
                                'title': 'Composants et props',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/Y2hgEGPzTZY',
                                'duration': 20,
                            },
                            {
                                'title': 'useState et gestion du state',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/O6P86uwfdR0',
                                'duration': 22,
                            },
                        ]
                    },
                    {
                        'title': 'Next.js 14 : App Router',
                        'description': 'Le futur de Next.js.',
                        'lessons': [
                            {
                                'title': 'Server Components vs Client Components',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/jjbHyuvKUQs',
                                'duration': 28,
                            },
                            {
                                'title': 'Routing avec App Router',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/6jQdZcYY3iU',
                                'duration': 24,
                            },
                            {
                                'title': 'Data fetching et Server Actions',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/xAgZhjupCpU',
                                'duration': 30,
                            },
                        ]
                    },
                    {
                        'title': 'Déploiement et optimisation',
                        'description': 'Mettre votre app en production.',
                        'lessons': [
                            {
                                'title': 'Performance et Core Web Vitals',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/lThL-6Ts1vs',
                                'duration': 20,
                            },
                            {
                                'title': 'Déployer sur Vercel',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/2HBIzEx6IZA',
                                'duration': 15,
                            },
                            {
                                'title': 'Monitoring et analytics',
                                'content_type': 'TEXT',
                                'duration': 12,
                                'text_content': 'Mise en place d\'outils de monitoring (Sentry, Vercel Analytics) pour surveiller la santé de votre application en production.',
                            },
                        ]
                    }
                ]
            },

            'Analyse de données avec Pandas': {
                'chapters': [
                    {
                        'title': 'Découvrir Pandas',
                        'description': 'Les structures de données fondamentales.',
                        'lessons': [
                            {
                                'title': 'Introduction à Pandas et installation',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/vmEHCJofslg',
                                'duration': 15,
                                'is_free_preview': True,
                            },
                            {
                                'title': 'Series et DataFrames',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/zmdjNSmRXF4',
                                'duration': 22,
                            },
                            {
                                'title': 'Lire et écrire des fichiers (CSV, Excel, JSON)',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/N6hyN6BW6ao',
                                'duration': 18,
                            },
                        ]
                    },
                    {
                        'title': 'Manipulation de données',
                        'description': 'Transformer, filtrer, agréger.',
                        'lessons': [
                            {
                                'title': 'Filtrage et sélection',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/Lw2rlcxScZY',
                                'duration': 20,
                            },
                            {
                                'title': 'GroupBy et agrégations',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/txMdrV1Ut64',
                                'duration': 25,
                            },
                            {
                                'title': 'Merge et jointures',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/iYWKfUOtGaw',
                                'duration': 22,
                            },
                        ]
                    },
                    {
                        'title': 'Visualisation et analyse',
                        'description': 'Donner du sens aux données.',
                        'lessons': [
                            {
                                'title': 'Plots avec Pandas et Matplotlib',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/UO98lJQ3QGI',
                                'duration': 20,
                            },
                            {
                                'title': 'Nettoyage de données',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/bDhvCp3_lYw',
                                'duration': 25,
                            },
                            {
                                'title': 'Cas pratique : analyser des ventes',
                                'content_type': 'VIDEO',
                                'video_url': 'https://www.youtube.com/embed/eMOA1pPVUc4',
                                'duration': 30,
                            },
                        ]
                    }
                ]
            },
        }

        # Appliquer les enrichissements
        updated_count = 0
        for course_title, data in enriched_data.items():
            try:
                course = Course.objects.get(title=course_title)
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠ Cours non trouvé : {course_title}'))
                continue

            # Supprimer anciens chapitres et recréer
            course.chapters.all().delete()

            for chapter_order, chapter_data in enumerate(data['chapters'], start=1):
                chapter = Chapter.objects.create(
                    course=course,
                    title=chapter_data['title'],
                    description=chapter_data.get('description', ''),
                    order=chapter_order,
                )

                for lesson_order, lesson_data in enumerate(chapter_data['lessons'], start=1):
                    Lesson.objects.create(
                        chapter=chapter,
                        title=lesson_data['title'],
                        content_type=lesson_data.get('content_type', 'VIDEO'),
                        video_url=lesson_data.get('video_url', ''),
                        text_content=lesson_data.get('text_content', ''),
                        duration_minutes=lesson_data.get('duration', 15),
                        is_free_preview=lesson_data.get('is_free_preview', False),
                        order=lesson_order,
                    )

            self.stdout.write(self.style.SUCCESS(f'  ✓ Enrichi : {course.title}'))
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ {updated_count} cours enrichis avec du contenu réel !'))
        self.stdout.write(self.style.SUCCESS('   Des vidéos YouTube éducatives ont été associées.'))
        self.stdout.write(self.style.SUCCESS('   Certaines leçons ont du contenu texte détaillé.\n'))