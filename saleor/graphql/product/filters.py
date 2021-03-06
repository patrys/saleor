import functools
import operator
from collections import defaultdict

from django import forms
from django.db.models import Q
from django_filters.constants import STRICTNESS
from django_filters.fields import Lookup
from graphene_django.filter.filterset import Filter, FilterSet

from ..fields import AttributeField
from ...product.models import Product, ProductAttribute


class DistinctFilterSet(FilterSet):
    # workaround for https://github.com/graphql-python/graphene-django/pull/290
    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all().distinct()
                return self._qs

            if not self.form.is_valid():
                if self.strict == STRICTNESS.RAISE_VALIDATION_ERROR:
                    raise forms.ValidationError(self.form.errors)
                elif self.strict == STRICTNESS.RETURN_NO_RESULTS:
                    self._qs = self.queryset.none()
                    return self._qs
                # else STRICTNESS.IGNORE...  ignoring

            # start with all the results and filter from there
            qs = self.queryset.all().distinct()
            for name, filter_ in self.filters.items():
                value = self.form.cleaned_data.get(name)

                if value is not None:  # valid & clean data
                    qs = filter_.filter(qs, value).distinct()

            self._qs = qs

        return self._qs


class ProduductAttributeFilter(Filter):
    field_class = AttributeField

    def filter(self, qs, value):
        if isinstance(value, Lookup):
            value = value.value

        if not value:
            return qs.distinct() if self.distinct else qs

        attributes = ProductAttribute.objects.prefetch_related('values')
        attributes_map = {
            attribute.slug: attribute.pk for attribute in attributes}
        values_map = {
            attr.slug: {value.slug: value.pk for value in attr.values.all()}
            for attr in attributes}
        queries = defaultdict(list)
        # Convert attribute:value pairs into a dictionary where
        # attributes are keys and values are grouped in lists
        for pair in value:
            attr_name, val_slug = pair.split(':', 1)
            if attr_name not in attributes_map:
                raise ValueError('Unknown attribute name: %r' % (attr_name, ))
            attr_pk = attributes_map[attr_name]
            attr_val_pk = values_map[attr_name].get(val_slug, val_slug)
            queries[attr_pk].append(attr_val_pk)
        # Combine filters of the same attribute with OR operator
        # and then combine full query with AND operator.
        combine_and = [
            functools.reduce(
                operator.or_, [
                    Q(**{'variants__attributes__%s' % (key, ): v}) |
                    Q(**{'attributes__%s' % (key, ): v}) for v in values])
            for key, values in queries.items()]
        query = functools.reduce(operator.and_, combine_and)
        qs = self.get_method(qs)(query)
        return qs.distinct() if self.distinct else qs


class ProductFilterSet(DistinctFilterSet):
    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'price': ['exact', 'range', 'lte', 'gte'],
            'attributes': ['exact']}

    @classmethod
    def filter_for_field(cls, f, field_name, lookup_expr='exact'):
        if field_name == 'attributes':
            return ProduductAttributeFilter(
                field_name=field_name, lookup_expr=lookup_expr, distinct=True)
        # this class method is called during class construction so we can't
        # reference ProductFilterSet here yet
        # pylint: disable=E1003
        return super(DistinctFilterSet, cls).filter_for_field(
            f, field_name, lookup_expr)
