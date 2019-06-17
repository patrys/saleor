import graphene
from graphene.types import ResolveInfo

from ...page import models
from ..core.resolvers import user_from_context
from ..utils import filter_by_query_param
from .types import Page

PAGE_SEARCH_FIELDS = ("content", "slug", "title")


def resolve_page(info: ResolveInfo, page_id=None, slug=None):
    assert page_id or slug, "No page ID or slug provided."
    user = user_from_context(info.context)

    if slug is not None:
        try:
            page = models.Page.objects.visible_to_user(user).get(slug=slug)
        except models.Page.DoesNotExist:
            page = None
    else:
        page = graphene.Node.get_node_from_global_id(info, page_id, Page)
        # Resolve to null if page is not published and user has no permission
        # to manage pages.
        is_available_to_user = (
            page and page.is_published or user.has_perm("page.manage_pages")
        )
        if not is_available_to_user:
            page = None
    return page


def resolve_pages(info: ResolveInfo, query):
    user = user_from_context(info.context)
    qs = models.Page.objects.visible_to_user(user)
    return filter_by_query_param(qs, query, PAGE_SEARCH_FIELDS)
