import logging

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from apps.cart.cart import Cart
from apps.cart.forms import CartAddProductForm
from apps.shop.models import Product

lg = logging.getLogger(__name__)


@require_POST
def add_card(request: WSGIRequest, product_id: int) -> HttpResponse:
    form = CartAddProductForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.add(
            product,
            quantity=int(cd['quantity']),
            override_quantity=bool(cd['override']),
        )

    return redirect('cart:detail')


@require_POST
def remove_card(request: WSGIRequest, product_id: int) -> HttpResponse:
    card = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    card.remove(product)
    return redirect('cart:detail')


@require_GET
def cart_detail(request: WSGIRequest) -> HttpResponse:
    cart = Cart(request)

    for product in cart:
        product['update_quality_form'] = CartAddProductForm(
            initial={
                'quantity': int(product["quantity"]),
                'override': True,
            }
        )

    template_name = 'cart/detail.html'
    return render(request, template_name, {'cart': cart})
