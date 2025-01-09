from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.db.models import Sum
from datetime import date
from .models import Transaction, MonthlySummary

# Señal personalizada para evitar el ciclo infinito
disable_signals = Signal()

@receiver(post_save, sender=Transaction)
def update_monthly_summary(sender, instance, **kwargs):
    """
    Actualiza el resumen mensual al guardar una transacción.
    """
    if disable_signals.receivers:  # Verifica si las señales están desactivadas
        return

    today = date.today()

    # Desactiva las señales temporalmente
    disable_signals.send(sender=sender)

    summary, created = MonthlySummary.objects.get_or_create(
        user=instance.user,
        year=today.year,
        month=today.month
    )

    # Recalcular los totales
    transactions = Transaction.objects.filter(
        user=instance.user,
        date__year=today.year,
        date__month=today.month
    )
    summary.total_income = transactions.filter(type="income").aggregate(Sum('amount'))['amount__sum'] or 0
    summary.total_expense = transactions.filter(type="expense").aggregate(Sum('amount'))['amount__sum'] or 0
    summary.balance = summary.total_income - summary.total_expense
    summary.save()

    # Reactiva las señales
    disable_signals.receivers = []
