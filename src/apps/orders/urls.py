from django.urls import path

from apps.orders.views import CreateOrderView, CreateOrderSuccessView

app_name = 'orders'

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create'),
    path('create/done/',
         CreateOrderSuccessView.as_view(),
         name='create_success')
]
