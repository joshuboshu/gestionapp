from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from django.db.models import Sum
from datetime import date
import pandas as pd
from .models import Transaction, MonthlySummary

@login_required
def transaction_list(request):
    """
    Vista para listar transacciones y calcular métricas financieras.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de transacciones renderizada.
    """
    today = date.today()

    # Transacciones del mes actual
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).order_by('-date')

    # Cálculos para el mes actual
    total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_income - total_expense

    # Historial mensual
    monthly_summaries = MonthlySummary.objects.filter(user=request.user).order_by('year', 'month')
    if monthly_summaries.exists():
        df = pd.DataFrame(list(monthly_summaries.values('year', 'month', 'total_income', 'total_expense', 'balance')))
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
        max_expense_month = df.loc[df['total_expense'].idxmax()]
        min_expense_month = df.loc[df['total_expense'].idxmin()]
    else:
        df = pd.DataFrame()
        max_expense_month = None
        min_expense_month = None

    # Contexto para la plantilla
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'monthly_summaries': monthly_summaries,
        'max_expense_month': max_expense_month,
        'min_expense_month': min_expense_month,
        'historical_data': df.to_dict(orient='records'),
    }

    # Manejar solicitudes HTMX
    if request.headers.get('HX-Request'):
        return render(request, 'transactions/_transaction_table.html', context)

    # Solicitudes normales
    return render(request, 'transactions/transaction_list.html', context)


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
