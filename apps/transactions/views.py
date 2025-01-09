from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Transaction
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from django.db.models import Sum
from datetime import date


@login_required
def transaction_list(request):
    """
    Vista para listar transacciones y calcular métricas financieras.

    Recupera las transacciones asociadas al usuario autenticado para el mes actual 
    y las ordena por fecha de manera descendente. Calcula el total de ingresos, 
    gastos y el balance mensual. Si la solicitud proviene de HTMX, renderiza 
    únicamente la tabla de transacciones; de lo contrario, renderiza toda la página.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de transacciones renderizada.
    """
    today = date.today()

    # Filtrar transacciones por usuario y mes actual
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).order_by('-date')

    # Calcular métricas financieras
    total_income = transactions.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = transactions.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0
    balance = total_income - total_expense

    # Verificar si la solicitud es HTMX
    if request.headers.get('HX-Request'):
        return render(
            request,
            'transactions/transaction_table.html',
            {
                'transactions': transactions,
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
            }
        )

    # Renderizar la página completa
    return render(
        request,
        'transactions/transaction_list.html',
        {
            'transactions': transactions,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
        }
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
