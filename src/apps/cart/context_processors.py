from django.core.handlers.wsgi import WSGIRequest

from apps.cart.cart import Cart


def cart(request: WSGIRequest) -> dict:
    return {'cart': Cart(request)}
