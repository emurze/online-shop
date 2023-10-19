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
from django.views.decorators.http import require_GET

from apps.cart.decorators import expire_success_token_redirect
from apps.orders.models import Order


lg = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class PaymentProcess(View):
    @expire_success_token_redirect
    def get(self, request: WSGIRequest) -> HttpResponse:
        order_id = cache.get(f'order_id_{request.session.session_key}')
        order = get_object_or_404(Order, id=order_id)
        context = {
            'order': order,
        }
        return render(request, 'payment/process.html', context)

    @expire_success_token_redirect
    def post(self, request: WSGIRequest) -> HttpResponse:
        order_id = cache.get(f'order_id_{request.session.session_key}')
        order = get_object_or_404(Order, id=order_id)

        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        for item in order.order_items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        lg.debug(f'{stripe.api_version}, {stripe.api_key}')

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)


@require_GET
def payment_completed(request: WSGIRequest) -> HttpResponse:
    return render(request, 'payment/completed.html')


@require_GET
def payment_canceled(request: WSGIRequest) -> HttpResponse:
    return render(request, 'payment/canceled.html')
