from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('payments/', views.payment_list, name='payment_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]