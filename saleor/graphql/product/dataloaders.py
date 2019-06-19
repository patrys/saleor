from collections import defaultdict
from typing import Any, Dict, List

from aiodataloader import DataLoader
from channels.db import database_sync_to_async

from ..core.resolvers import user_from_context
from ...discount import DiscountInfo
from ...discount.models import Sale
from ...product import models


class DjangoLoader(DataLoader):
    context_key = None

    def __init__(self, *args, context, user, **kwargs):
        self.context = context
        self.user = user
        super().__init__(*args, **kwargs)

    async def batch_load_fn(self, keys):
        objects = await self.batch_load(keys)
        pk_map = {
            (o[0] if isinstance(o, tuple) else o.pk): (
                o[1] if isinstance(o, tuple) else o
            )
            for o in objects
        }
        return [pk_map.get(key, None) for key in keys]

    @database_sync_to_async
    def batch_load(self, keys: List[Any]):
        return list(self.batch_query(keys))

    def batch_query(self, keys):
        raise NotImplementedError()

    @classmethod
    def for_context(cls, context: Dict):
        key = cls.context_key
        if key is None:
            raise TypeError("Data loader %r does not define a context key" % (cls,))
        loaders = context.setdefault("loaders", {})
        if key not in loaders:
            user = user_from_context(context)
            loaders[key] = cls(context=context, user=user)
        loader = loaders[key]
        assert isinstance(loader, cls)
        return loader


class CategoryLoader(DjangoLoader):
    context_key = "category"

    def batch_query(self, keys):
        return models.Category.objects.filter(pk__in=keys)


class SalesLoader(DjangoLoader):
    context_key = "sales"

    def batch_query(self, keys):
        return [
            (
                date,
                Sale.objects.active(date).prefetch_related(
                    "products", "categories", "collections"
                ),
            )
            for date in keys
        ]


class ProductImageLoader(DjangoLoader):
    context_key = "product/images"

    def batch_query(self, keys):
        images = models.ProductImage.objects.filter(product_id__in=keys)
        image_map = defaultdict(list)
        for image in images:
            image_map[image.product_id].append(image)
        return image_map.items()


class DiscountsLoader(DjangoLoader):
    context_key = "discounts"

    def fetch_categories(self, sale_pks):
        categories = Sale.categories.through.objects.filter(
            sale_id__in=sale_pks
        ).values_list("sale_id", "category_id")
        category_map = defaultdict(set)
        for sale_pk, category_pk in categories:
            category_map[sale_pk].add(category_pk)
        subcategory_map = defaultdict(set)
        for sale_pk, category_pks in category_map.items():
            subcategory_map[sale_pk] = set(
                models.Category.tree.filter(pk__in=category_pks)
                .get_descendants(include_self=True)
                .values_list("pk", flat=True)
            )
        return subcategory_map

    def fetch_collections(self, sale_pks):
        collections = Sale.collections.through.objects.filter(
            sale_id__in=sale_pks
        ).values_list("sale_id", "collection_id")
        collection_map = defaultdict(set)
        for sale_pk, collection_pk in collections:
            collection_map[sale_pk].add(collection_pk)
        return collection_map

    def fetch_products(self, sale_pks):
        products = Sale.products.through.objects.filter(
            sale_id__in=sale_pks
        ).values_list("sale_id", "product_id")
        product_map = defaultdict(set)
        for sale_pk, product_pk in products:
            product_map[sale_pk].add(product_pk)
        return product_map

    def batch_query(self, keys):
        sales_map = list((date, list(Sale.objects.active(date))) for date in keys)
        pks = {s.pk for d, ss in sales_map for s in ss}
        collections = self.fetch_collections(pks)
        products = self.fetch_products(pks)
        categories = self.fetch_categories(pks)

        return [
            (
                date,
                [
                    DiscountInfo(
                        sale=sale,
                        category_ids=categories[sale.pk],
                        collection_ids=collections[sale.pk],
                        product_ids=products[sale.pk],
                    )
                    for sale in sales
                ],
            )
            for date, sales in sales_map
        ]
