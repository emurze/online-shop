from django.urls import path

from apps.orders.views import (
    CreateOrderView,
    admin_order_detail,
    admin_order_pdf
)

app_name = 'orders'

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create'),
    path('admin/order/<slug:order_id>/',
         admin_order_detail,
         name='admin_order_detail'),
    path('admin/order/pdf/<slug:order_id>',
         admin_order_pdf,
         name='admin_order_pdf')
]
