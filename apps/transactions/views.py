import numpy as np
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from .models import Transaction, MonthlySummary
import json
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import TransactionForm

def get_month_name(month_number):
    """
    Convierte el número de mes a su nombre correspondiente en español.

    Args:
        month_number (int): Número del mes (1-12).

    Returns:
        str: Nombre del mes en español.
    """
    months_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    return months_es.get(month_number, '')


@login_required
def transaction_list(request):
    """
    Vista para listar transacciones y generar análisis financiero.

    Calcula los ingresos, gastos y balance del mes actual.
    Además, procesa un historial mensual de resúmenes financieros y genera
    datos para gráficos y estadísticas avanzadas.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Respuesta HTTP con el contexto renderizado en el template.
    """
    today = date.today()

    # Obtener transacciones del mes actual
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).order_by('-date')

    # Calcular ingresos, gastos y balance del mes actual
    total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_income - total_expense

    # Obtener datos históricos
    monthly_summaries = MonthlySummary.objects.filter(user=request.user).order_by('year', 'month')

    stats = {}
    chart_data = {'labels': [], 'income': [], 'expense': [], 'balance': []}
    expense_distribution = {}
    historical_data = []

    if monthly_summaries.exists():
        df = pd.DataFrame(list(monthly_summaries.values()))

        if not df.empty:
            # Convertir el número del mes a su nombre correspondiente
            df['month_name'] = df['month'].apply(get_month_name)
            df['balance'] = df['total_income'] - df['total_expense']

            # Validar datos para cálculos avanzados
            if len(df) > 1 and df['total_income'].notnull().all() and df['total_expense'].notnull().all():
                try:
                    stats = {
                        'avg_income': df['total_income'].mean(),
                        'avg_expense': df['total_expense'].mean(),
                        'max_income_month': df.loc[df['total_income'].idxmax(), 'month_name'],
                        'max_expense_month': df.loc[df['total_expense'].idxmax(), 'month_name'],
                        'trend_income': np.polyfit(range(len(df)), df['total_income'], 1)[0],
                        'trend_expense': np.polyfit(range(len(df)), df['total_expense'], 1)[0],
                    }
                except np.linalg.LinAlgError:
                    # Si `np.polyfit` falla, establecer valores predeterminados
                    stats['trend_income'] = 0
                    stats['trend_expense'] = 0

            # Preparar datos para gráficos
            chart_data = {
                'labels': df['month_name'].tolist(),
                'income': df['total_income'].tolist(),
                'expense': df['total_expense'].tolist(),
                'balance': df['balance'].tolist()
            }

            # Distribución de gastos promedio
            expense_distribution = df.groupby('month_name')['total_expense'].mean().to_dict()

            # Actualizar historical_data con nombres de meses
            historical_data = df[['year', 'month_name', 'total_income', 'total_expense', 'balance']].to_dict(orient='records')

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'stats': stats,
        'chart_data': json.dumps(chart_data),
        'expense_distribution': json.dumps(expense_distribution),
        'historical_data': historical_data  # Ahora incluye nombres de meses
    }

    if request.headers.get('HX-Request'):
        return render(request, 'transactions/_transaction_table.html', context)

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
