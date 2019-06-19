from typing import Dict, Iterable

from django.contrib.sites.models import Site
from starlette.requests import Request

from ...account.models import User
from ...discount import DiscountInfo


def request_from_context(context: Dict) -> Request:
    return context["request"]


def currency_from_context(context: Dict) -> str:
    request = request_from_context(context)
    return request["currency"]


def site_from_context(context: Dict) -> Site:
    request = request_from_context(context)
    return request["site"]


def discounts_from_context(context: Dict) -> Iterable[DiscountInfo]:
    request = request_from_context(context)
    return request["discounts"]


def taxes_from_context(context: Dict) -> Dict:
    request = request_from_context(context)
    return request["taxes"]


def user_from_context(context: Dict) -> User:
    request = request_from_context(context)
    return request.user
