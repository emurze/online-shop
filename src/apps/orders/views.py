import logging

from .tasks import log_message
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
    success_url = reverse_lazy('orders:create_success')
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

        log_message.delay()

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
