import logging

import redis
from django.conf import settings
from django.db.models import QuerySet

from apps.shop.models import Product

lg = logging.getLogger(__name__)
conn = redis.Redis(
    db=settings.RECOMMENDATION_SYSTEM['DB'],
    port=settings.RECOMMENDATION_SYSTEM['PORT'],
    host=settings.RECOMMENDATION_SYSTEM['HOST'],
)


class ProductRecommender:
    """Store and update and retrieve items"""

    @staticmethod
    def _get_product_key(product_id) -> str:
        return f'product:{product_id}:purchases_with'

    def clear_purchases(self):
        conn.delete(*(
            self._get_product_key(_id)
            for _id in Product.objects.values_list('id', flat=True)
        ))

    def set_product_bought(self, products: QuerySet[Product]) -> None:
        product_ids = [product.id for product in products]

        for product_id in product_ids:
            for another_id in product_ids:
                if product_id != another_id:
                    conn.zincrby(
                        self._get_product_key(product_id),
                        1,
                        another_id
                    )

    def get_recommendations(
            self,
            products: list,
            max_results: int = 6
    ) -> list:

        if len(products) == 1:
            product_key = self._get_product_key(products[0].id)
            suggestion_ids = [
                int(_id.decode(settings.ENCODING))
                for _id in conn.zrange(
                    product_key, 0, -1, desc=True
                )[:max_results]
            ]
        else:
            product_ids = (str(product.id) for product in products)
            keys = [self._get_product_key(flat_id) for flat_id in product_ids]

            tmp_key = f'tmp_{keys}'

            conn.zunionstore(tmp_key, keys)  # Get union of all keys products
            conn.zrem(tmp_key, *product_ids)

            suggestion_ids = [
                int(_id.decode(settings.ENCODING))
                for _id in conn.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            ]
            conn.delete(tmp_key)

        suggestion_products = list(
            Product.objects.filter(id__in=suggestion_ids)
        )
        suggestion_products.sort(key=lambda x: suggestion_ids.index(x.id))
        return suggestion_products
