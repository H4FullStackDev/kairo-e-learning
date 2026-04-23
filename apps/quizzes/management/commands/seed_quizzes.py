from django.core.management.base import BaseCommand
from apps.courses.models import Course
from apps.quizzes.models import Quiz, Question, Answer


class Command(BaseCommand):
    help = 'Crée des quiz de démonstration pour les cours'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🧠 Génération des quiz...\n'))

        quizzes_data = {
            'Introduction au Machine Learning': {
                'title': 'Quiz final : Maîtrisez-vous le ML ?',
                'description': 'Testez vos connaissances sur les fondamentaux du Machine Learning.',
                'quiz_type': 'COURSE_FINAL',
                'passing_score': 70,
                'questions': [
                    {
                        'text': "Quelle est la différence principale entre l'apprentissage supervisé et non-supervisé ?",
                        'type': 'SINGLE',
                        'points': 2,
                        'explanation': "L'apprentissage supervisé utilise des données étiquetées (avec une réponse connue), tandis que le non-supervisé travaille sur des données brutes sans étiquettes.",
                        'answers': [
                            {'text': "Le supervisé utilise des données étiquetées, le non-supervisé non", 'correct': True},
                            {'text': "Le supervisé est plus rapide", 'correct': False},
                            {'text': "Le non-supervisé utilise plus de mémoire", 'correct': False},
                            {'text': "Il n'y a aucune différence", 'correct': False},
                        ]
                    },
                    {
                        'text': "Parmi ces algorithmes, lesquels sont utilisés en apprentissage supervisé ? (plusieurs réponses possibles)",
                        'type': 'MULTIPLE',
                        'points': 3,
                        'explanation': "La régression linéaire et les arbres de décision sont supervisés. K-Means et DBSCAN sont des algorithmes de clustering (non-supervisés).",
                        'answers': [
                            {'text': "Régression linéaire", 'correct': True},
                            {'text': "Arbre de décision", 'correct': True},
                            {'text': "K-Means", 'correct': False},
                            {'text': "DBSCAN", 'correct': False},
                        ]
                    },
                    {
                        'text': "scikit-learn est la bibliothèque de référence pour le Deep Learning.",
                        'type': 'TRUE_FALSE',
                        'points': 1,
                        'explanation': "scikit-learn est principalement pour le ML classique. Pour le Deep Learning, on utilise PyTorch ou TensorFlow.",
                        'answers': [
                            {'text': "Vrai", 'correct': False},
                            {'text': "Faux", 'correct': True},
                        ]
                    },
                    {
                        'text': "Quelle méthode utilise-t-on pour évaluer un modèle de classification ?",
                        'type': 'SINGLE',
                        'points': 2,
                        'explanation': "L'accuracy (taux d'exactitude) est la métrique de base. D'autres métriques comme précision, recall, F1-score existent aussi.",
                        'answers': [
                            {'text': "Accuracy (taux d'exactitude)", 'correct': True},
                            {'text': "La dérivée partielle", 'correct': False},
                            {'text': "Le produit matriciel", 'correct': False},
                            {'text': "La variance croisée", 'correct': False},
                        ]
                    },
                    {
                        'text': "Qu'est-ce que le 'overfitting' (surapprentissage) ?",
                        'type': 'SINGLE',
                        'points': 2,
                        'explanation': "Le overfitting se produit quand le modèle apprend trop par cœur les données d'entraînement et perd sa capacité à généraliser sur de nouvelles données.",
                        'answers': [
                            {'text': "Le modèle apprend trop par cœur et ne généralise plus", 'correct': True},
                            {'text': "Le modèle est trop simple", 'correct': False},
                            {'text': "Le modèle prend trop de RAM", 'correct': False},
                            {'text': "Le modèle a trop peu de données", 'correct': False},
                        ]
                    },
                ]
            },
            'Django pour les débutants': {
                'title': 'Quiz final : Avez-vous maîtrisé Django ?',
                'description': 'Évaluez votre compréhension du framework Django.',
                'quiz_type': 'COURSE_FINAL',
                'passing_score': 70,
                'questions': [
                    {
                        'text': "Que signifie l'acronyme MVT dans Django ?",
                        'type': 'SINGLE',
                        'points': 1,
                        'explanation': "Django utilise le pattern MVT : Model (données), View (logique métier), Template (présentation).",
                        'answers': [
                            {'text': "Model View Template", 'correct': True},
                            {'text': "Model View Terminal", 'correct': False},
                            {'text': "Module View Transform", 'correct': False},
                            {'text': "Main View Target", 'correct': False},
                        ]
                    },
                    {
                        'text': "Quelle commande permet de créer une nouvelle app Django ?",
                        'type': 'SINGLE',
                        'points': 2,
                        'explanation': "`python manage.py startapp` crée une nouvelle app dans le projet. `startproject` crée un projet entier.",
                        'answers': [
                            {'text': "python manage.py startapp nom_app", 'correct': True},
                            {'text': "django create app nom_app", 'correct': False},
                            {'text': "python manage.py newapp nom_app", 'correct': False},
                            {'text': "django-admin startapp nom_app", 'correct': False},
                        ]
                    },
                    {
                        'text': "Lesquelles de ces affirmations sur l'ORM Django sont vraies ? (plusieurs réponses)",
                        'type': 'MULTIPLE',
                        'points': 3,
                        'explanation': "L'ORM Django permet d'interagir avec la BDD en Python, génère les requêtes SQL automatiquement, et supporte plusieurs SGBD.",
                        'answers': [
                            {'text': "Il permet d'écrire des requêtes en Python au lieu du SQL", 'correct': True},
                            {'text': "Il génère le SQL automatiquement", 'correct': True},
                            {'text': "Il fonctionne avec PostgreSQL, MySQL, SQLite, etc.", 'correct': True},
                            {'text': "Il ne fonctionne qu'avec Oracle", 'correct': False},
                        ]
                    },
                    {
                        'text': "Il est obligatoire de créer des migrations après chaque modification d'un modèle.",
                        'type': 'TRUE_FALSE',
                        'points': 1,
                        'explanation': "Chaque modification structurelle d'un modèle (ajout de champ, changement de type, etc.) nécessite `makemigrations` puis `migrate`.",
                        'answers': [
                            {'text': "Vrai", 'correct': True},
                            {'text': "Faux", 'correct': False},
                        ]
                    },
                    {
                        'text': "Quel fichier contient les routes (URLs) d'un projet Django ?",
                        'type': 'SINGLE',
                        'points': 1,
                        'explanation': "Le fichier `urls.py` contient la configuration des routes. Il y en a un par projet et potentiellement un par app.",
                        'answers': [
                            {'text': "urls.py", 'correct': True},
                            {'text': "routes.py", 'correct': False},
                            {'text': "paths.py", 'correct': False},
                            {'text': "config.py", 'correct': False},
                        ]
                    },
                ]
            },
            'React & Next.js 14': {
                'title': 'Quiz : Testez vos connaissances React & Next.js',
                'description': 'Un quiz pour valider votre maîtrise de React et Next.js.',
                'quiz_type': 'COURSE_FINAL',
                'passing_score': 70,
                'questions': [
                    {
                        'text': "Qu'est-ce que JSX ?",
                        'type': 'SINGLE',
                        'points': 1,
                        'explanation': "JSX est une extension de syntaxe JavaScript qui permet d'écrire du HTML dans le JavaScript, compilée par Babel.",
                        'answers': [
                            {'text': "Une extension de syntaxe qui permet d'écrire du HTML dans du JS", 'correct': True},
                            {'text': "Un langage de programmation à part", 'correct': False},
                            {'text': "Un format de fichier pour les images", 'correct': False},
                            {'text': "Une base de données NoSQL", 'correct': False},
                        ]
                    },
                    {
                        'text': "Quels hooks React sont les plus utilisés ? (plusieurs réponses)",
                        'type': 'MULTIPLE',
                        'points': 2,
                        'explanation': "useState pour le state local, useEffect pour les effets de bord, useContext pour le contexte. useRouter est spécifique à Next.js.",
                        'answers': [
                            {'text': "useState", 'correct': True},
                            {'text': "useEffect", 'correct': True},
                            {'text': "useContext", 'correct': True},
                            {'text': "useDatabase", 'correct': False},
                        ]
                    },
                    {
                        'text': "Dans Next.js 14 App Router, les composants sont par défaut :",
                        'type': 'SINGLE',
                        'points': 2,
                        'explanation': "Dans le App Router de Next.js 14, les composants sont par défaut des Server Components. Il faut ajouter 'use client' pour en faire des Client Components.",
                        'answers': [
                            {'text': "Server Components", 'correct': True},
                            {'text': "Client Components", 'correct': False},
                            {'text': "Static Components", 'correct': False},
                            {'text': "Hybrid Components", 'correct': False},
                        ]
                    },
                ]
            },
            'Analyse de données avec Pandas': {
                'title': 'Quiz : Maîtrisez-vous Pandas ?',
                'description': 'Évaluation de vos compétences en manipulation de données avec Pandas.',
                'quiz_type': 'COURSE_FINAL',
                'passing_score': 70,
                'questions': [
                    {
                        'text': "Quelle est la structure de données principale de Pandas pour les données tabulaires ?",
                        'type': 'SINGLE',
                        'points': 1,
                        'explanation': "Le DataFrame est la structure principale, organisée en lignes et colonnes comme un tableau Excel.",
                        'answers': [
                            {'text': "DataFrame", 'correct': True},
                            {'text': "Series", 'correct': False},
                            {'text': "Array", 'correct': False},
                            {'text': "Matrix", 'correct': False},
                        ]
                    },
                    {
                        'text': "Quelle méthode utilise-t-on pour lire un fichier CSV ?",
                        'type': 'SINGLE',
                        'points': 1,
                        'explanation': "pd.read_csv() est la fonction dédiée à la lecture de CSV avec de nombreuses options (séparateur, encoding, etc.).",
                        'answers': [
                            {'text': "pd.read_csv()", 'correct': True},
                            {'text': "pd.open_csv()", 'correct': False},
                            {'text': "pd.load_csv()", 'correct': False},
                            {'text': "pd.import_csv()", 'correct': False},
                        ]
                    },
                    {
                        'text': "Quelles opérations sont possibles avec groupby() ? (plusieurs réponses)",
                        'type': 'MULTIPLE',
                        'points': 3,
                        'explanation': "groupby permet d'effectuer toutes les agrégations classiques : somme, moyenne, comptage, min/max.",
                        'answers': [
                            {'text': "sum() - somme", 'correct': True},
                            {'text': "mean() - moyenne", 'correct': True},
                            {'text': "count() - comptage", 'correct': True},
                            {'text': "delete() - suppression", 'correct': False},
                        ]
                    },
                ]
            }
        }

        for course_title, quiz_data in quizzes_data.items():
            try:
                course = Course.objects.get(title=course_title)
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠ Cours non trouvé : {course_title}'))
                continue

            # Supprimer l'ancien quiz final s'il existe
            Quiz.objects.filter(course=course, quiz_type=quiz_data['quiz_type']).delete()

            # Créer le quiz
            quiz = Quiz.objects.create(
                course=course,
                title=quiz_data['title'],
                description=quiz_data['description'],
                quiz_type=quiz_data['quiz_type'],
                passing_score=quiz_data['passing_score'],
                is_active=True,
            )

            # Créer les questions
            for q_order, q_data in enumerate(quiz_data['questions'], start=1):
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['text'],
                    question_type=q_data['type'],
                    points=q_data['points'],
                    explanation=q_data.get('explanation', ''),
                    order=q_order,
                )

                for a_order, a_data in enumerate(q_data['answers'], start=1):
                    Answer.objects.create(
                        question=question,
                        text=a_data['text'],
                        is_correct=a_data['correct'],
                        order=a_order,
                    )

            self.stdout.write(self.style.SUCCESS(f'  ✓ Quiz créé : {quiz.title} ({quiz.total_questions} questions)'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Génération terminée !\n'))