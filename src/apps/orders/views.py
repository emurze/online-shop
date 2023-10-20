import logging

import weasyprint
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

from .tasks import order_created
from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from apps.cart.cart import Cart
from apps.cart.decorators import (
    empty_cart_redirect,
    expire_success_token_redirect
)
from apps.orders.forms import OrderCreateForm
from apps.orders.models import Order, OrderItem

lg = logging.getLogger(__name__)


class CreateOrderView(CreateView):
    success_url = reverse_lazy('payment:process')
    template_name = 'orders/create.html'
    form_class = OrderCreateForm
    model = Order

    @empty_cart_redirect
    def get(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @empty_cart_redirect
    def post(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: OrderCreateForm) -> HttpResponse:
        order = form.save()
        cart = Cart(self.request)

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                price=product['price'],
                product=product['instance'],
                quantity=product['quantity'],
            )
            for product in cart
        ])

        cart.clear()

        """Set temporary session_key to get success page"""
        cache.set(f'order_id_{self.request.session.session_key}', order.id,
                  timeout=settings.SUCCESS_ORDER_CACHE_EXPIRATION)

        order_created.delay(order.id)

        return super().form_valid(form)


class CreateOrderSuccessView(TemplateView):
    template_name = 'orders/created.html'

    @expire_success_token_redirect
    def get(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['order_id'] = cache.get(
            f'order_id_{self.request.session.session_key}'
        )
        return super().get_context_data(**kwargs)


@require_GET
@staff_member_required
def admin_order_detail(request: WSGIRequest, order_id: str) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    template_name = 'orders/admin/detail.html'
    return render(request, template_name, {'order': order})


@require_GET
@staff_member_required
def admin_order_pdf(request: WSGIRequest, order_id: str) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    template_name = 'orders/admin/pdf.html'
    html = render_to_string(template_name, {'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['CONTENT-DISPOSITION'] = f'filename={order_id}.pdf'

    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=(settings.STATIC_ROOT / 'css/pdf.css',),
    )
    return response
