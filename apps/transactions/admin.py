from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Transaction en el panel de administración de Django.

    - `list_display`: Campos que se mostrarán como columnas en la lista de transacciones.
    - `list_filter`: Filtros que aparecerán en la barra lateral para facilitar la búsqueda.
    - `search_fields`: Campos que serán buscables mediante la barra de búsqueda.

    Permite a los administradores gestionar las transacciones de manera eficiente.
    """
    list_display = ('user', 'type', 'category', 'amount', 'date')
    list_filter = ('type', 'category', 'date')
    search_fields = ('category', 'description')
