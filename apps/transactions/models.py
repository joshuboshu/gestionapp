from django.db import models
from django.conf import settings

class Transaction(models.Model):
    """
    Modelo para representar una transacción financiera.

    Atributos:
        user (ForeignKey): Relación con el usuario que realizó la transacción.
        type (CharField): Tipo de transacción, puede ser 'income' (ingreso) o 'expense' (gasto).
        category (CharField): Categoría de la transacción (e.g., 'Alimentos', 'Transporte').
        amount (DecimalField): Monto de la transacción.
        description (TextField): Descripción opcional de la transacción.
        date (DateField): Fecha en que ocurrió la transacción.
        created_at (DateTimeField): Fecha y hora en que se creó el registro.
        updated_at (DateTimeField): Fecha y hora en que se actualizó el registro por última vez.

    Métodos:
        __str__: Devuelve una representación legible del objeto en formato "tipo - monto (categoría)".
    """
    TYPE_CHOICES = (
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    category = models.CharField(
        max_length=50
    )
    amount = models.IntegerField()
    description = models.TextField(
        blank=True,
        null=True
    )
    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        """
        Devuelve una representación legible del objeto.

        Ejemplo:
            "income - 1500.00 (Salary)"
        """
        return f"{self.type} - {self.amount} ({self.category})"

class MonthlySummary(models.Model):
    """
    Modelo para almacenar estadísticas mensuales de transacciones.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monthly_summaries'
    )
    year = models.IntegerField()
    month = models.IntegerField()
    total_income = models.IntegerField()
    total_expense = models.IntegerField()
    balance = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'year', 'month')

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}"
