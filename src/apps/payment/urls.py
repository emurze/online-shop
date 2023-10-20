from django.urls import path

from apps.payment.views import (
    PaymentProcess,
    PaymentCanceled,
    PaymentCompleted
)
from apps.payment.webhooks import stripe_webhook

app_name = 'payment'

urlpatterns = [
    path('process/', PaymentProcess.as_view(), name='process'),
    path('completed/', PaymentCompleted.as_view(), name='completed'),
    path('canceled/', PaymentCanceled.as_view(), name='canceled'),
    path('webhook/', stripe_webhook, name='stripe_webhook')
]
