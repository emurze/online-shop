import csv
import datetime
from typing import Any

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe, SafeString

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


def order_payment(obj: Order) -> Any | SafeString:
    if payment_id := obj.payment_id:
        url = obj.get_payment_url()
        html = f'<a href="{url}" target="_blank">{payment_id}</a>'
        return mark_safe(html)
    else:
        return ''


def order_detail(obj: Order) -> Any | SafeString:
    message = 'View'
    url = reverse('orders:admin_order_detail', args=(str(obj.id),))
    return mark_safe(f'<a href="{url}">{message}</a>')


def order_pdf(obj: Order) -> Any | SafeString:
    message = 'PDF'
    url = reverse('orders:admin_order_pdf', args=(str(obj.id),))
    return mark_safe(f'<a href="{url}">{message}</a>')


def export_to_csv(
    model_admin: ModelAdmin,
    request: WSGIRequest,
    queryset: QuerySet
) -> HttpResponse:

    options = model_admin.model._meta
    content_disposition = f'attachment; filename={options.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition

    writer = csv.writer(response)
    fields = [field for field in options.get_fields()
              if not field.many_to_many and not field.one_to_many]

    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])

    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)

    return response


export_to_csv.short_description = 'Export to CSV'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'address',
        'postal_code',
        'city',
        order_payment,
        'paid',
        order_detail,
        order_pdf,
    )
    list_editable = ('paid',)
    inlines = (OrderItemInline,)
    actions = (export_to_csv,)
