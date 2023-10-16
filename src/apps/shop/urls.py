from django.urls import path

from apps.shop.views import ProductList, ProductFilterList, ProductDetail

app_name = 'shop'

urlpatterns = [
    path('', ProductList.as_view()),
    path('products/', ProductList.as_view(), name='list'),
    path('products/<slug:category_slug>/',
         ProductFilterList.as_view(),
         name='list_by_category_slug'),
    path('product/<int:id>/<slug:slug>',
         ProductDetail.as_view(),
         name='detail')
]
