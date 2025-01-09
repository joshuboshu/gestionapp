from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    """
    Formulario personalizado para crear o editar transacciones.
    """
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'date']
        labels = {
            'type': 'Tipo de Transacción',
            'category': 'Categoría',
            'amount': 'Monto',
            'description': 'Descripción',
            'date': 'Fecha',
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
