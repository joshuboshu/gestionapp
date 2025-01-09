from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    """
    Vista basada en clase para registrar un nuevo usuario.
    """
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Autentica al usuario después del registro.
        """
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response


def login_view(request):
    """
    Vista basada en función para iniciar sesión.
    """
    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import authenticate, login

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('transaction_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """
    Cierra la sesión del usuario y redirige al login.
    """
    logout(request)
    return redirect('login')
