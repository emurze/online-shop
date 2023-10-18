import functools
from collections.abc import Callable

from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect

from apps.cart.cart import Cart


def empty_cart_redirect(func: Callable) -> Callable:
    @functools.wraps(func)
    def http_method(self, request: WSGIRequest, *args, **kwargs):
        cart = Cart(request)

        """Cart must have at least 1 elem"""
        if not len(cart) != 0:
            return redirect(settings.MAIN_PAGE_REDIRECT)

        return func(self, request, *args, **kwargs)

    return http_method


def expire_success_token_redirect(func: Callable) -> Callable:
    @functools.wraps(func)
    def http_method(self, request: WSGIRequest, *args, **kwargs):
        """Cache must include order_id"""
        if not cache.get(f'order_id_{request.session.session_key}'):
            return redirect(settings.MAIN_PAGE_REDIRECT)

        return func(self, request, *args, **kwargs)

    return http_method
