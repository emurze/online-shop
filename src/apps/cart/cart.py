import logging
from _decimal import Decimal

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

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

        cart = self.session.get(settings.SESSION_CART_ID)
        if not cart:
            cart = self.session[settings.SESSION_CART_ID] = {}

        self.cart = cart

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

        lg.debug(override_quantity)

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
        return sum(int(product['quantity']) for product in self.cart.values())

    def get_total_price(self) -> int:
        return sum(
            Decimal(product['price']) * int(product['quantity'])
            for product in self.cart.values()
        )

    def clear(self):
        del self.session[settings.SESSION_CART_ID]
        self.save()

    def __str__(self) -> str:
        return str(self.cart)


