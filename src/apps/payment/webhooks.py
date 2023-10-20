import enum
import logging

import stripe
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from stripe.error import SignatureVerificationError

from apps.orders.models import Order
from .tasks import payment_completed

lg = logging.getLogger(__name__)


class PaymentEvent(enum.StrEnum):
    COMPLETED = 'checkout.session.completed'
    CANCELED = 'checkout.session.canceled'


@csrf_exempt
def stripe_webhook(request: WSGIRequest):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event.type == PaymentEvent.COMPLETED:
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            order.paid = True
            order.payment_id = session.payment_intent
            order.save()

            payment_completed.delay(order.id)

    return HttpResponse(status=200)
