# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Max


class SortableSerializerMixin(object):
    """
    Add this class to serializers responsible
    """
    def __init__(self, *args, **kwargs):
        self.default_order_field = self.Meta.model.Meta.ordering[0].lstrip('-')
        super(SortableSerializerMixin, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data[]
        # self.base_model.objects.aggregate(
        #    max_order=Max(self.default_order_field)
        # )['max_order'] or 0
        # TODO: add a mixin for max_order
        return super(SortableSerializerMixin, self).create(validated_data)

    def get_max_order(self, request, obj=None):
        max_order = self.Meta.model.objects.aggregate(
            max_order=Max(self.default_order_field)
        )['max_order'] or 0
        return max_order


class PolymorphicSerializerMixin(SortableSerializerMixin):
    """
    If the admin class is used for a polymorphic model, hence inherits from
    ``PolymorphicParentModelAdmin`` rather than ``admin.ModelAdmin``, then
    additionally inherit from ``PolymorphicSerializerMixin`` rather than
    ``SortableSerializerMixin``.
    """
    def get_max_order(self, request, obj=None):
        return self.base_model.objects.aggregate(
            max_order=Max(self.default_order_field)
        )['max_order'] or 0
