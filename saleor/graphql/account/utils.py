from django.core.exceptions import ValidationError
from graphene.types import ResolveInfo

from ..core.resolvers import user_from_context
from ...account import events as account_events


class UserDeleteMixin:
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info: ResolveInfo, instance):
        user = user_from_context(info.context)
        if instance == user:
            raise ValidationError({"id": "You cannot delete your own account."})
        elif instance.is_superuser:
            raise ValidationError({"id": "Cannot delete this account."})


class CustomerDeleteMixin(UserDeleteMixin):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance):
        super().clean_instance(info, instance)
        if instance.is_staff:
            raise ValidationError({"id": "Cannot delete a staff account."})

    @classmethod
    def post_process(cls, info: ResolveInfo, deleted_count=1):
        account_events.staff_user_deleted_a_customer_event(
            staff_user=user_from_context(info.context), deleted_count=deleted_count
        )


class StaffDeleteMixin(UserDeleteMixin):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance):
        super().clean_instance(info, instance)
        if not instance.is_staff:
            raise ValidationError({"id": "Cannot delete a non-staff user."})
