from django.db import models
from django.utils import timezone
from decimal import Decimal

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")

    def __str__(self):
        return self.name

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('UNPAID', 'Non payée'),
        ('PARTIAL', 'Partiellement payée'),
        ('PAID', 'Payée'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', verbose_name="Client")
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="N° de facture")
    date = models.DateField(default=timezone.now, verbose_name="Date")
    due_date = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00'), verbose_name="Taux TVA (%)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID', verbose_name="Statut")

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.client.name}"

    @property
    def total_ht(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_vat(self):
        return (self.total_ht * self.vat_rate) / 100

    @property
    def total_ttc(self):
        return self.total_ht + self.total_vat

    @property
    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def balance_due(self):
        return self.total_ttc - self.amount_paid

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255, verbose_name="Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire HT")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name="Facture")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    date = models.DateField(default=timezone.now, verbose_name="Date de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence / Moyen de paiement")

    def __str__(self):
        return f"Paiement de {self.amount} pour {self.invoice.invoice_number}"
