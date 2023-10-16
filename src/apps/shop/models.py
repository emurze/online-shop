from django.db import models
from django.db.models import QuerySet
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)

    class Meta:
        ordering = ('name',)
        indexes = (
            models.Index(fields=('name',)),
        )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('shop:list_by_category_slug', args=(self.slug,))


class AvailableProducts(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(available=True)


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.SET_NULL,
                                 null=True)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    image = models.ImageField(upload_to='product/%Y/%m/%d', blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    only_available = AvailableProducts()

    class Meta:
        ordering = ('-created',)
        indexes = (
            models.Index(fields=('id', 'slug')),
            models.Index(fields=('-created',))
        )
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('shop:detail', args=(self.id, self.slug),)

