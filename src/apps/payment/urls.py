from django.urls import path

from apps.payment.views import (
    PaymentProcess,
    payment_canceled,
    payment_completed
)

app_name = 'payment'

urlpatterns = [
    path('process/', PaymentProcess.as_view(), name='process'),
    path('completed/', payment_completed, name='completed'),
    path('canceled/', payment_canceled, name='canceled'),
]
