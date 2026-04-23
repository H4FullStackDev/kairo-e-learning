from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import User


class HomeView(TemplateView):
    """Page d'accueil."""
    template_name = 'accounts/home.html'


class RegisterView(CreateView):
    """Vue d'inscription."""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Bienvenue {form.cleaned_data['first_name']} ! Votre compte a été créé avec succès. Connectez-vous maintenant."
        )
        return response

    def dispatch(self, request, *args, **kwargs):
        # Rediriger si déjà connecté
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """Vue de connexion personnalisée."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name()} !")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Déconnexion."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vue du profil utilisateur."""
    template_name = 'accounts/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vue de modification du profil."""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return super().form_valid(form)