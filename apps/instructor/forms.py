from django import forms
from django.utils.text import slugify
from apps.courses.models import Course, Category, Chapter, Lesson


class CourseForm(forms.ModelForm):
    """Formulaire pour créer ou éditer un cours."""

    class Meta:
        model = Course
        fields = [
            'title', 'short_description', 'description', 'category',
            'thumbnail', 'trailer_video', 'level', 'price',
            'duration_hours', 'objectives', 'prerequisites',
            'status', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'kairos-input',
                'placeholder': 'Ex : Introduction au Machine Learning',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 2,
                'placeholder': 'Une phrase accrocheuse de 1-2 lignes...',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 8,
                'placeholder': 'Décrivez en détail le contenu, le public cible, ce que les étudiants vont apprendre...',
            }),
            'category': forms.Select(attrs={
                'class': 'kairos-input',
            }),
            'level': forms.Select(attrs={
                'class': 'kairos-input',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 0,
                'step': 100,
                'placeholder': '0 pour gratuit',
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 0,
                'placeholder': 'Durée totale estimée (heures)',
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 4,
                'placeholder': 'Listez les objectifs pédagogiques (un par ligne)',
            }),
            'prerequisites': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 3,
                'placeholder': 'Connaissances requises avant de suivre ce cours',
            }),
            'status': forms.Select(attrs={
                'class': 'kairos-input',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'kairos-checkbox',
            }),
        }
        labels = {
            'title': 'Titre du cours',
            'short_description': 'Description courte',
            'description': 'Description complète',
            'category': 'Catégorie',
            'thumbnail': 'Image de couverture',
            'trailer_video': 'Vidéo de présentation (URL YouTube)',
            'level': 'Niveau',
            'price': 'Prix (FCFA)',
            'duration_hours': 'Durée totale (heures)',
            'objectives': 'Objectifs pédagogiques',
            'prerequisites': 'Prérequis',
            'status': 'Statut',
            'is_featured': 'Mettre en avant sur la page d\'accueil',
        }
        help_texts = {
            'short_description': '200 caractères maximum. Apparaît sur les cartes du catalogue.',
            'thumbnail': 'Format conseillé : 1280x720px (16:9). Max 5MB.',
            'trailer_video': 'Lien YouTube optionnel pour présenter le cours en vidéo.',
            'is_featured': 'Réservé aux administrateurs.',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrer les catégories actives uniquement
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = '— Choisir une catégorie —'

        # Restreindre is_featured aux admins
        if self.user and not self.user.is_superuser:
            self.fields.pop('is_featured', None)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
        return title

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return price



class ChapterForm(forms.ModelForm):
    """Formulaire pour créer/éditer un chapitre."""

    class Meta:
        model = Chapter
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'kairos-input',
                'placeholder': 'Ex : Les fondamentaux du Machine Learning',
            }),
            'description': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 3,
                'placeholder': 'Décrivez brièvement le contenu de ce chapitre...',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1,
            }),
        }
        labels = {
            'title': 'Titre du chapitre',
            'description': 'Description',
            'order': 'Position',
        }
        help_texts = {
            'order': 'Ordre d\'apparition dans le cours (1 = premier).',
        }

class LessonForm(forms.ModelForm):
    """Formulaire pour créer/éditer une leçon."""

    class Meta:
        model = Lesson
        fields = [
            'title', 'content_type', 'order',
            'duration_minutes', 'video', 'video_url',
            'pdf_file', 'text_content', 'is_free_preview',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'kairos-input',
                'placeholder': 'Ex : Qu\'est-ce que le Machine Learning ?',
            }),
            'content_type': forms.Select(attrs={
                'class': 'kairos-input',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1,
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1,
                'placeholder': '15',
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'kairos-input',
                'placeholder': 'https://www.youtube.com/watch?v=...',
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 10,
                'placeholder': 'Rédigez ici le contenu de la leçon. Vous pouvez utiliser du texte simple.',
            }),
            'is_free_preview': forms.CheckboxInput(attrs={
                'class': 'kairos-checkbox',
            }),
        }
        labels = {
            'title': 'Titre de la leçon',
            'content_type': 'Type de contenu',
            'order': 'Position',
            'duration_minutes': 'Durée estimée (minutes)',
            'video': 'Fichier vidéo (upload)',
            'video_url': 'URL vidéo (YouTube/Vimeo)',
            'pdf_file': 'Fichier PDF',
            'text_content': 'Contenu texte',
            'is_free_preview': 'Aperçu gratuit',
        }
        help_texts = {
            'duration_minutes': 'Estimation de la durée pour l\'étudiant.',
            'video': 'Upload direct (max 100MB). Préférez l\'URL pour de meilleures performances.',
            'video_url': 'Recommandé : utilisez une URL YouTube pour une meilleure expérience.',
            'is_free_preview': 'Si coché, cette leçon sera visible sans inscription au cours.',
        }

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        video = cleaned_data.get('video')
        video_url = cleaned_data.get('video_url')
        pdf_file = cleaned_data.get('pdf_file')
        text_content = cleaned_data.get('text_content')

        if content_type == 'VIDEO' and not (video or video_url):
            raise forms.ValidationError(
                "Pour une leçon vidéo, vous devez fournir une URL ou uploader un fichier."
            )
        elif content_type == 'PDF' and not pdf_file:
            raise forms.ValidationError(
                "Pour une leçon PDF, vous devez uploader un fichier."
            )
        elif content_type == 'TEXT' and not text_content:
            raise forms.ValidationError(
                "Pour une leçon texte, vous devez écrire du contenu."
            )

        return cleaned_data



from apps.quizzes.models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    """Formulaire pour créer/éditer un quiz (version sûre)."""

    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'quiz_type', 'chapter',
            'passing_score', 'time_limit_minutes', 'max_attempts',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'kairos-input',
                'placeholder': 'Ex : Quiz final · Introduction au ML',
            }),
            'description': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 3,
                'placeholder': 'Décrivez l\'objectif de ce quiz...',
            }),
            'quiz_type': forms.Select(attrs={'class': 'kairos-input'}),
            'chapter': forms.Select(attrs={'class': 'kairos-input'}),
            'passing_score': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 0, 'max': 100,
                'placeholder': '70',
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 0,
                'placeholder': '30 (laisser vide pour pas de limite)',
            }),
            'max_attempts': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1,
                'placeholder': '3',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'kairos-checkbox'}),
        }
        labels = {
            'title': 'Titre du quiz',
            'description': 'Description',
            'quiz_type': 'Type de quiz',
            'chapter': 'Chapitre lié (optionnel)',
            'passing_score': 'Score minimum pour réussir (%)',
            'time_limit_minutes': 'Limite de temps (minutes)',
            'max_attempts': 'Nombre maximum de tentatives',
            'is_active': 'Quiz actif (visible par les étudiants)',
        }
        help_texts = {
            'quiz_type': 'CHAPTER : à la fin d\'un chapitre. FINAL : à la fin du cours.',
            'chapter': 'Requis pour les quiz de type CHAPTER.',
            'time_limit_minutes': 'Laissez vide pour aucune limite de temps.',
            'max_attempts': 'Nombre de fois qu\'un étudiant peut passer ce quiz.',
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['chapter'].queryset = Chapter.objects.filter(course=course).order_by('order')
            self.fields['chapter'].empty_label = '— Aucun (quiz final du cours) —'

class QuestionForm(forms.ModelForm):
    """Formulaire pour créer/éditer une question."""

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'order', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 3,
                'placeholder': 'Tapez votre question ici...',
            }),
            'question_type': forms.Select(attrs={'class': 'kairos-input'}),
            'points': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1, 'max': 100,
            }),
            'order': forms.NumberInput(attrs={
                'class': 'kairos-input',
                'min': 1,
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'kairos-input',
                'rows': 3,
                'placeholder': 'Expliquez la réponse correcte (visible après que l\'étudiant a répondu)...',
            }),
        }
        labels = {
            'text': 'Question',
            'question_type': 'Type de question',
            'points': 'Points',
            'order': 'Position',
            'explanation': 'Explication',
        }
        help_texts = {
            'question_type': 'SINGLE : 1 seule bonne réponse. MULTIPLE : plusieurs bonnes réponses. TRUE_FALSE : Vrai/Faux.',
            'explanation': 'L\'explication aide les étudiants à comprendre. Optionnel.',
        }