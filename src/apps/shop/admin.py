from django.contrib import admin
from django.utils.html import format_html

from apps.shop.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'loaded_image', 'price',
        'available', 'created', 'updated'
    )
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'available')
    prepopulated_fields = {'slug': ('name',)}

    @staticmethod
    def loaded_image(instance: Product) -> str:
        try:
            attributes_dict = {
                'height': 100,
                'width': 100,
            }
            attributes = ''.join(
                f'{k}={v}' for k, v in attributes_dict.items())
            return format_html(
                f'<img src="{instance.image.url}" alt="" {attributes}>')
        except ValueError:
            return 'no image'
