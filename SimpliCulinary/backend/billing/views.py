from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Client, Invoice, InvoiceItem, Payment
from .forms import ClientForm, InvoiceForm, InvoiceItemFormSet, PaymentForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime, timedelta

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'billing/client_list.html', {'clients': clients})

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client created successfully.')
            return redirect('billing:client_list')
    else:
        form = ClientForm()
    return render(request, 'billing/client_form.html', {'form': form})

def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            # Calculate subtotal
            subtotal = sum(item.total for item in invoice.items.all())
            invoice.subtotal = subtotal
            invoice.save()
            messages.success(request, 'Invoice created successfully.')
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    return render(request, 'billing/invoice_form.html', {'form': form, 'formset': formset})

def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # PDF content
    p.drawString(100, 750, f"Invoice: {invoice.invoice_number}")
    p.drawString(100, 730, f"Client: {invoice.client.name}")
    p.drawString(100, 710, f"Date: {invoice.date}")
    p.drawString(100, 690, f"Due Date: {invoice.due_date}")
    
    y = 650
    p.drawString(100, y, "Description")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Unit Price")
    p.drawString(450, y, "Total")
    y -= 20
    
    for item in invoice.items.all():
        p.drawString(100, y, item.description)
        p.drawString(300, y, str(item.quantity))
        p.drawString(350, y, str(item.unit_price))
        p.drawString(450, y, str(item.total))
        y -= 20
    
    p.drawString(350, y-20, f"Subtotal: {invoice.subtotal}")
    p.drawString(350, y-40, f"VAT ({invoice.vat_rate}%): {invoice.vat_amount}")
    p.drawString(350, y-60, f"Total: {invoice.total}")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'billing/payment_list.html', {'payments': payments})

def dashboard(request):
    # Monthly revenue
    now = timezone.now()
    start_of_month = now.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    monthly_revenue = Payment.objects.filter(date__range=(start_of_month, end_of_month)).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Total unpaid invoices
    unpaid_invoices = Invoice.objects.filter(status__in=['sent', 'overdue'])
    
    context = {
        'monthly_revenue': monthly_revenue,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'billing/dashboard.html', context)
