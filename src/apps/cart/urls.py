from django.urls import path

from apps.cart.views import cart_detail, add_card, remove_card

app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='detail'),
    path('add/<int:product_id>/', add_card, name='add'),
    path('remove/<int:product_id>/', remove_card, name='remove'),
]
