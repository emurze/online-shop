import decimal
import uuid
from _decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.coupons.models import Coupon
from apps.shop.models import Product


class Order(models.Model):
    """
    1. Contains User info and it paid or not.
    2. get_total_cost - obtain the total price of items bought in the order
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    address = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=256)
    city = models.CharField(max_length=128)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    payment_id = models.CharField(max_length=256, null=True)
    paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True)
    discount = models.IntegerField(
        validators=(
            MinValueValidator(0),
            MaxValueValidator(100),
        ),
        help_text='percent value (0 to 100)'
    )

    class Meta:
        ordering = ('-created',)
        indexes = (
            models.Index(fields=('-created',)),
        )

    def __str__(self) -> str:
        return f'Order {self.id}'

    def get_total_cost_before_discount(self) -> decimal:
        return sum(item.get_cost() for item in self.order_items.all())

    def get_discount(self) -> decimal:
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return self.discount / Decimal(100) * total_cost
        return Decimal(0)

    def get_total_cost(self):
        return self.get_total_cost_before_discount() - self.get_discount()

    def get_payment_url(self):
        if not self.payment_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.payment_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return str(self.id)

    def get_cost(self) -> decimal:
        return self.price * self.quantity
