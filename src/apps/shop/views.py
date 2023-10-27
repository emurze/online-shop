import logging

from django.db.models import QuerySet
from django.views.generic import DetailView

from apps.shop.mixins import BaseProductList, AddCartAddProductFormMixin, \
    AddRecommendProducts
from apps.shop.models import Product

lg = logging.getLogger(__name__)


class ProductList(BaseProductList):
    def get_queryset(self) -> QuerySet:
        return Product.only_available.all()


class ProductFilterList(BaseProductList):
    queryset = (
        Product
        .only_available
        .select_related('category')
    )

    def get_queryset(self) -> QuerySet:
        products = self.queryset

        category_slug: str | None = self.kwargs.get('category_slug')
        if category_slug is not None:
            products = products.filter(category__slug=category_slug)

        return products


class ProductDetail(
    AddCartAddProductFormMixin,
    AddRecommendProducts,
    DetailView
):
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product/detail.html'
