from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Transaction
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm


@login_required
def transaction_list(request):
    """
    Vista basada en función para listar transacciones.

    Recupera las transacciones asociadas al usuario autenticado y las ordena
    por fecha de manera descendente. Si la solicitud proviene de HTMX, renderiza
    únicamente la tabla de transacciones; de lo contrario, renderiza toda la página.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de transacciones renderizada.
    """
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    if request.headers.get('HX-Request'):
        # Renderiza solo la tabla si es una solicitud HTMX
        return render(
            request,
            'transactions/transaction_table.html',
            {'transactions': transactions}
        )
    # Renderiza toda la página
    return render(
        request,
        'transactions/transaction_list.html',
        {'transactions': transactions}
    )


class TransactionCreateView(CreateView):
    """
    Vista basada en clase para crear una nueva transacción.

    Permite al usuario registrar un ingreso o un gasto mediante un formulario.
    Una vez creado, se redirige a la lista de transacciones.

    Atributos:
        model (Transaction): Modelo asociado a la vista.
        fields (list): Campos que se mostrarán en el formulario.
        template_name (str): Ruta de la plantilla HTML utilizada.
        success_url (str): URL a la que se redirige después de guardar con éxito.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        """
        Método para validar el formulario antes de guardar.

        Asigna automáticamente el usuario autenticado como propietario
        de la transacción.

        Args:
            form (ModelForm): El formulario con los datos enviados.

        Returns:
            HttpResponse: Respuesta HTTP tras guardar con éxito.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)
