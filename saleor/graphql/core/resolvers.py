from starlette.requests import Request
from graphene import ResolveInfo

from ...account.models import User


def resolve_request(info: ResolveInfo) -> Request:
    return info.context["request"]


def resolve_user(info: ResolveInfo) -> User:
    request = resolve_request(info)
    return request.user
