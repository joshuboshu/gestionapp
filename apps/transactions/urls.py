from django.urls import path
from .views import transaction_list, TransactionCreateView

urlpatterns = [
    path('', transaction_list, name='transaction_list'),
    path('add/', TransactionCreateView.as_view(), name='transaction_add'),
]
