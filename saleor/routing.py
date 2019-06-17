import datetime

from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.middleware import BaseMiddleware
from channels.routing import URLRouter
from django.urls.conf import re_path
from django.utils.functional import SimpleLazyObject
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.graphql import GraphQLApp

from .graphql.api import schema
from .core.utils.taxes import get_taxes_for_country
from .core.utils import get_country_by_ip, get_currency_for_country


def get_discounts():
    from .discount.models import Sale

    return Sale.objects.active(datetime.date.today()).prefetch_related(
        "products", "categories", "collections"
    )


def get_taxes(country):
    return get_taxes_for_country(country)


def get_country(scope):
    from django.conf import settings
    from django_countries.fields import Country

    ip = scope.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        return ip.split(",")[0].strip()
    ip = scope.get("REMOTE_ADDR", None)
    if ip:
        return get_country_by_ip(ip)
    return Country(settings.DEFAULT_COUNTRY)


def get_currency(country):
    from django.conf import settings

    if country is not None:
        return get_currency_for_country(country)
    else:
        return settings.DEFAULT_CURRENCY


def get_site():
    from django.contrib.sites.models import Site

    Site.objects.clear_cache()
    return Site.objects.get_current()


class SaleorMiddleware(BaseMiddleware):
    def populate_scope(self, scope):
        scope["country"] = SimpleLazyObject(lambda: get_country(scope))
        scope["currency"] = SimpleLazyObject(lambda: get_currency(scope["country"]))
        scope["discounts"] = SimpleLazyObject(get_discounts)
        scope["site"] = SimpleLazyObject(get_site)
        scope["taxes"] = SimpleLazyObject(lambda: get_taxes(scope["country"]))

    async def resolve_scope(self, scope):
        pass


class SaleorGraphQLApp(GraphQLApp):
    """Work around the fact that Daphne is still ASGI 2."""

    def __call__(self, scope) -> None:
        async def handle(receive, send):
            await super(SaleorGraphQLApp, self).__call__(scope, receive, send)

        return handle


application = URLRouter(
    [
        # re_path(
        #     "^graphql/",
        #     AuthMiddlewareStack(
        #         SaleorMiddleware(
        #             SaleorGraphQLApp(schema=schema, executor_class=AsyncioExecutor)
        #         )
        #     ),
        # ),
        re_path("", AsgiHandler)
    ]
)
