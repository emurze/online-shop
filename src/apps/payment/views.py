import logging
from _decimal import Decimal

import stripe
from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.cart.decorators import expire_success_token_redirect
from apps.orders.models import Order


lg = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class PaymentProcess(View):
    template_name = 'payment/process.html'

    @expire_success_token_redirect
    def get(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        context = {'order': self._get_order_from_cache()}
        return render(request, self.template_name, context)

    @expire_success_token_redirect
    def post(self, request: WSGIRequest) -> HttpResponse:
        order = self._get_order_from_cache()

        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [
                {
                    'price_data': {
                        'unit_amount': int(order_item.price * Decimal('100')),
                        'currency': 'usd',
                        'product_data': {
                            'name': order_item.product.name,
                        },
                    },
                    'quantity': order_item.quantity,
                }
                for order_item in order.order_items.all()
            ]
        }

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    def _get_order_from_cache(self) -> Order:
        order_id = cache.get(f'order_id_{self.request.session.session_key}')
        order = get_object_or_404(Order, id=order_id)
        return order


class PaymentCompleted(TemplateView):
    template_name = 'payment/completed.html'


class PaymentCanceled(TemplateView):
    template_name = 'payment/canceled.html'
