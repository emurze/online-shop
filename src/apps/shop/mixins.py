import logging

from django.views.generic import ListView, TemplateView

from apps.cart.forms import CartAddProductForm
from apps.shop.models import Category
from utils.mixin_for import mixin_for

lg = logging.getLogger(__name__)


class CategoryMixin(mixin_for(ListView)):
    def get_context_data(self, **kwargs):
        kwargs['categories'] = Category.objects.all()

        category_slug = self.kwargs.get('category_slug')
        if category_slug is not None:
            kwargs['current_category_slug'] = category_slug

        return super().get_context_data(**kwargs)


class AddCartAddProductFormMixin(mixin_for(TemplateView)):
    def get_context_data(self, **kwargs):
        kwargs['add_cart_form'] = CartAddProductForm()
        return super().get_context_data(**kwargs)


class BaseProductList(CategoryMixin, ListView):
    context_object_name = 'products'
    template_name = 'shop/product/list.html'
