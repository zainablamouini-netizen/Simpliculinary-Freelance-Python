from django.contrib import admin
from .models import Client, Invoice, InvoiceItem, Payment

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'date', 'status', 'total_ht', 'total_ttc', 'balance_due')
    list_filter = ('status', 'date', 'client')
    search_fields = ('invoice_number', 'client__name')
    inlines = [InvoiceItemInline, PaymentInline]
    readonly_fields = ('total_ht', 'total_vat', 'total_ttc', 'amount_paid', 'balance_due')

    fieldsets = (
        (None, {
            'fields': ('client', 'invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('date', 'due_date')
        }),
        ('Taxes', {
            'fields': ('vat_rate',)
        }),
        ('Calculs (Lecture seule)', {
            'fields': ('total_ht', 'total_vat', 'total_ttc', 'amount_paid', 'balance_due')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'date', 'reference')
    list_filter = ('date',)
    search_fields = ('invoice__invoice_number', 'reference')
