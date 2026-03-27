from django import forms
from django.forms import modelformset_factory
from .models import Client, Invoice, InvoiceItem, Payment

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'address', 'phone']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_number', 'date', 'due_date', 'vat_rate']

InvoiceItemFormSet = modelformset_factory(InvoiceItem, fields=['description', 'quantity', 'unit_price'], extra=1)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'date', 'method', 'notes']