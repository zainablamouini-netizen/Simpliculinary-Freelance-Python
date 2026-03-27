from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Client, Invoice, Payment
import datetime
import io

class ClientListView(ListView):
    model = Client
    template_name = 'invoices/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(CreateView):
    model = Client
    fields = ['name', 'email', 'phone', 'address']
    template_name = 'invoices/client_form.html'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(UpdateView):
    model = Client
    fields = ['name', 'email', 'phone', 'address']
    template_name = 'invoices/client_form.html'
    success_url = reverse_lazy('client_list')

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {'invoice': invoice, 'today': timezone.now()}
    pdf = render_to_pdf('invoices/invoice_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Facture_{invoice.invoice_number}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erreur lors de la génération du PDF", status=400)

def dashboard(request):
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    
    # Last 6 months income
    monthly_income = []
    for i in range(6):
        month_date = first_day_of_month - datetime.timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
            
        income = Payment.objects.filter(date__gte=month_start, date__lt=month_end).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_income.append({
            'month': month_start.strftime('%B %Y'),
            'amount': income
        })

    # Stats
    total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    pending_amount = sum(inv.balance_due for inv in Invoice.objects.filter(status__in=['UNPAID', 'PARTIAL']))
    client_count = Client.objects.count()
    invoice_count = Invoice.objects.count()

    context = {
        'monthly_income': reversed(monthly_income),
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'client_count': client_count,
        'invoice_count': invoice_count,
    }
    return render(request, 'invoices/dashboard.html', context)
