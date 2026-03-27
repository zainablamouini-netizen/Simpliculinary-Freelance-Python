from django.contrib import admin
from .models import Client, Invoice, InvoiceItem, Payment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'date', 'due_date', 'total', 'status')
    list_filter = ('status', 'date')
    search_fields = ('invoice_number', 'client__name')

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'date', 'method')
    list_filter = ('date', 'method')
