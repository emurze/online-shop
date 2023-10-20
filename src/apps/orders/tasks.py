import logging

from celery import shared_task
from django.core.mail import send_mail

from apps.orders.models import Order

lg = logging.getLogger(__name__)


@shared_task
def order_created(order_id: int) -> None:
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'
    send_mail(
        subject,
        message,
        'adm1@adm1.com',
        (order.email,),
    )
