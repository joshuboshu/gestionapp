from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para registrar usuarios.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar textos de ayuda
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario personalizado para iniciar sesión.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
