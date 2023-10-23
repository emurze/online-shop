from django.urls import path

from apps.coupons.views import coupon_apply_view

app_name = 'coupons'

urlpatterns = [
    path('apply/', coupon_apply_view, name='apply'),
]
