import decimal
import logging
from _decimal import Decimal
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest

from apps.coupons.models import Coupon
from apps.shop.models import Product

lg = logging.getLogger(__name__)


class Cart:
    """
    self.cart = {
        42: {
            'price': 324,
            'quantity': 1,
        }
    }
    """

    def __init__(self, request: WSGIRequest) -> None:
        """Get cart from session or set to session"""

        self.session = request.session
        self.session_key = self.session.session_key

        cart = self.session.get(settings.SESSION_CART_ID)
        if not cart:
            cart = self.session[settings.SESSION_CART_ID] = {}

        self.cart = cart
        self.coupon_id = cache.get(
            f'{settings.SESSION_COUPON_ID}_{self.session_key}'
        )

    def __iter__(self):
        """
        1. Query products.
        2. Return dict with products with
             - product - instance
             - Decimal(price)
             - Decimal(full_price)
        """

        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['instance'] = product

        for product in cart.values():
            product['price'] = Decimal(product['price'])
            product['full_price'] = (
                Decimal(product['price']) * int(product['quantity'])
            )
            yield product

    def add(self, product: Product, quantity: int = 1,
            override_quantity: bool = False) -> None:
        """Add product or increase quantity of product"""

        product_id = str(product.id)

        if not self.cart.get(product_id):
            self.cart[product_id] = {
                'quantity': str(quantity),
                'price': str(product.price),
            }
        else:
            if override_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] = (
                    int(self.cart[product_id]['quantity']) + quantity
                )

        self.save()

    def save(self) -> None:
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """Remove product from cart"""

        product_id = str(product.id)
        if self.cart.get(product_id):
            del self.cart[product_id]
            self.save()

    def __len__(self) -> int:
        """Get total quantity"""
        return sum(
            (int(product['quantity']) for product in self.cart.values()),
            start=0
        )

    def get_total_price(self) -> int:
        return sum(
            Decimal(product['price']) * int(product['quantity'])
            for product in self.cart.values()
        )

    def clear(self):
        del self.session[settings.SESSION_CART_ID]
        self.save()

    @property
    def coupon(self) -> Coupon | None:
        if self.coupon_id:
            try:
                coupon = Coupon.objects.get(id=self.coupon_id)
                return coupon
            except Coupon.DoesNotExist:
                return None
        else:
            return None

    def get_discount(self) -> decimal:
        if self.coupon:
            return (self.coupon.discount / Decimal(100) *
                    Decimal(self.get_total_price()))
        else:
            return Decimal(0)

    def get_total_price_after_discount(self) -> decimal:
        return self.get_total_price() - self.get_discount()

    def __str__(self) -> str:
        return str(self.cart)
