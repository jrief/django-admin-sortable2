# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from itertools import chain
from types import MethodType

from django import forms
from django.contrib.admin.views.main import ORDER_VAR
# Remove check when support for python < 3 is dropped.
import sys
if sys.version_info[0] >= 3:
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.contrib import admin, messages
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
try:
    from django.urls import reverse
except ImportError:  # Django<1.11
    from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.db.models.aggregates import Max
from django.db.models.expressions import F
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, pre_save
from django.forms.models import BaseInlineFormSet
from django.forms import widgets
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseForbidden)

__all__ = ['SortableAdminMixin', 'SortableInlineAdminMixin']


def _get_default_ordering(model, model_admin):
    try:
        # first try with the model admin ordering
        none, prefix, field_name = model_admin.ordering[0].rpartition('-')
    except (AttributeError, IndexError, TypeError):
        pass
    else:
        return prefix, field_name

    try:
        # then try with the model ordering
        none, prefix, field_name = model._meta.ordering[0].rpartition('-')
    except (AttributeError, IndexError):
        msg = "Model {0}.{1} requires a list or tuple 'ordering' in its Meta class"
        raise ImproperlyConfigured(msg.format(model.__module__, model.__name__))
    else:
        return prefix, field_name


class MovePageActionForm(admin.helpers.ActionForm):
    step = forms.IntegerField(
        required=False,
        initial=1,
        widget=widgets.NumberInput(attrs={'id': 'changelist-form-step'}),
        label=False)
    page = forms.IntegerField(
        required=False,
        widget=widgets.NumberInput(attrs={'id': 'changelist-form-page'}),
        label=False)


class SortableAdminBase(object):
    @property
    def media(self):
        css = {'all': ['adminsortable2/css/sortable.css']}
        js = [
            'admin/js/jquery.init.js',
            'adminsortable2/js/plugins/admincompat.js',
            'adminsortable2/js/libs/jquery.ui.core-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.widget-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.mouse-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.touch-punch-0.2.3.js',
            'adminsortable2/js/libs/jquery.ui.sortable-1.11.4.js',
        ]
        return super(SortableAdminBase, self).media + widgets.Media(css=css, js=js)


class SortableAdminMixin(SortableAdminBase):
    BACK, FORWARD, FIRST, LAST, EXACT = range(5)
    action_form = MovePageActionForm

    @property
    def change_list_template(self):
        opts = self.model._meta
        app_label = opts.app_label
        return [
            os.path.join('adminsortable2', app_label, opts.model_name, 'change_list.html'),
            os.path.join('adminsortable2', app_label, 'change_list.html'),
            'adminsortable2/change_list.html'
        ]

    def __init__(self, model, admin_site):
        self.default_order_direction, self.default_order_field = _get_default_ordering(model, self)
        super(SortableAdminMixin, self).__init__(model, admin_site)
        self.enable_sorting = False
        self.order_by = None
        if not isinstance(self.exclude, (list, tuple)):
            self.exclude = [self.default_order_field]
        elif not self.exclude or self.default_order_field != self.exclude[0]:
            self.exclude = [self.default_order_field] + list(self.exclude)
        if isinstance(self.list_display_links, (list, tuple)) and len(self.list_display_links) == 0:
            self.list_display_links = [self.list_display[0]]
        self._add_reorder_method()
        self.list_display = list(self.list_display)

        # Insert the magic field into the same position as the first occurrence
        # of the default_order_field, or, if not present, at the start
        try:
            self.default_order_field_index = self.list_display.index(self.default_order_field)
        except ValueError:
            self.default_order_field_index = 0
        self.list_display.insert(self.default_order_field_index, '_reorder')

        # Remove *all* occurrences of the field from `list_display`
        if self.list_display and self.default_order_field in self.list_display:
            self.list_display = [f for f in self.list_display if f != self.default_order_field]

        # Remove *all* occurrences of the field from `list_display_links`
        if self.list_display_links and self.default_order_field in self.list_display_links:
            self.list_display_links = [f for f in self.list_display_links if f != self.default_order_field]

        # Remove *all* occurrences of the field from `ordering`
        if self.ordering and self.default_order_field in self.ordering:
            self.ordering = [f for f in self.ordering if f != self.default_order_field]
        rev_field = '-' + self.default_order_field
        if self.ordering and rev_field in self.ordering:
            self.ordering = [f for f in self.ordering if f != rev_field]

    def _get_update_url_name(self):
        return '%s_%s_sortable_update' % (self.model._meta.app_label, self.model._meta.model_name)

    def get_urls(self):
        my_urls = [
            url(r'^adminsortable2_update/$',
                self.admin_site.admin_view(self.update_order),
                name=self._get_update_url_name()),
        ]
        return my_urls + super(SortableAdminMixin, self).get_urls()

    def get_actions(self, request):
        actions = super(SortableAdminMixin, self).get_actions(request)
        paginator = self.get_paginator(request, self.get_queryset(request), self.list_per_page)
        if len(paginator.page_range) > 1 and 'all' not in request.GET and self.enable_sorting:
            # add actions for moving items to other pages
            move_actions = ['move_to_exact_page']
            cur_page = int(request.GET.get('p', 0)) + 1
            if len(paginator.page_range) > 2 and cur_page > paginator.page_range[1]:
                move_actions.append('move_to_first_page')
            if cur_page > paginator.page_range[0]:
                move_actions.append('move_to_back_page')
            if cur_page < paginator.page_range[-1]:
                move_actions.append('move_to_forward_page')
            if len(paginator.page_range) > 2 and cur_page < paginator.page_range[-2]:
                move_actions.append('move_to_last_page')
            for fname in move_actions:
                actions.update({fname: self.get_action(fname)})
        return actions

    def get_changelist(self, request, **kwargs):
        first_order_direction, first_order_field_index = self._get_first_ordering(request)
        if first_order_field_index == self.default_order_field_index:
            self.enable_sorting = True
            self.order_by = "{}{}".format(first_order_direction, self.default_order_field)
        else:
            self.enable_sorting = False
        return super(SortableAdminMixin, self).get_changelist(request, **kwargs)

    def _get_first_ordering(self, request):
        """
        Must be consistent with `django.contrib.admin.views.main.ChangeList.get_ordering`.
        """
        order_var = request.GET.get(ORDER_VAR)
        if order_var is None:
            first_order_field_index = self.default_order_field_index
            first_order_direction = self.default_order_direction
        else:
            first_order_field_index = None
            first_order_direction = ""
            for p in order_var.split("."):
                none, prefix, index = p.rpartition("-")
                try:
                    index = int(index)
                except ValueError:
                    continue  # skip it
                else:
                    first_order_field_index = index - 1
                    first_order_direction = prefix
                    break
        return first_order_direction, first_order_field_index

    @property
    def media(self):
        m = super(SortableAdminMixin, self).media
        if self.enable_sorting:
            m = m + widgets.Media(js=[
                'adminsortable2/js/libs/jquery.ui.sortable-1.11.4.js',
                'adminsortable2/js/list-sortable.js',
            ])
        return m

    def _add_reorder_method(self):
        """
        Adds a bound method, named '_reorder' to the current instance of this class, with attributes
        allow_tags, short_description and admin_order_field.
        This can only be done using a function, since it is not possible to add dynamic attributes
        to bound methods.
        """
        def func(this, item):
            html = ''
            if this.enable_sorting:
                html = '<div class="drag js-reorder-{1}" order="{0}">&nbsp;</div>'.format(getattr(item, this.default_order_field), item.pk)
            return mark_safe(html)

        setattr(func, 'allow_tags', True)
        # if the field used for ordering has a verbose name use it, otherwise default to "Sort"
        for order_field in self.model._meta.fields:
            if order_field.name == self.default_order_field:
                short_description = getattr(order_field, 'verbose_name', None)
                if short_description:
                    setattr(func, 'short_description', short_description)
                    break
        else:
            setattr(func, 'short_description', _('Sort'))
        setattr(func, 'admin_order_field', self.default_order_field)
        setattr(self, '_reorder', MethodType(func, self))

    def update_order(self, request):
        if not request.is_ajax() or request.method != 'POST':
            return HttpResponseBadRequest('Not an XMLHttpRequest')
        if request.method != 'POST':
            return HttpResponseNotAllowed('Must be a POST request')
        if not self.has_change_permission(request):
            return HttpResponseForbidden('Missing permissions to perform this request')
        startorder = int(request.POST.get('startorder'))
        endorder = int(request.POST.get('endorder', 0))
        moved_items = list(self._move_item(request, startorder, endorder))
        return HttpResponse(json.dumps(moved_items, cls=DjangoJSONEncoder), content_type='application/json;charset=UTF-8')

    def save_model(self, request, obj, form, change):
        if not change:
            setattr(obj, self.default_order_field, self.get_max_order(request, obj) + 1)
        super(SortableAdminMixin, self).save_model(request, obj, form, change)

    def move_to_exact_page(self, request, queryset):
        self._bulk_move(request, queryset, self.EXACT)
    move_to_exact_page.short_description = _('Move selected to specific page')

    def move_to_back_page(self, request, queryset):
        self._bulk_move(request, queryset, self.BACK)
    move_to_back_page.short_description = _('Move selected ... pages back')

    def move_to_forward_page(self, request, queryset):
        self._bulk_move(request, queryset, self.FORWARD)
    move_to_forward_page.short_description = _('Move selected ... pages forward')

    def move_to_first_page(self, request, queryset):
        self._bulk_move(request, queryset, self.FIRST)
    move_to_first_page.short_description = _('Move selected to first page')

    def move_to_last_page(self, request, queryset):
        self._bulk_move(request, queryset, self.LAST)
    move_to_last_page.short_description = _('Move selected to last page')

    def _move_item(self, request, startorder, endorder):
        extra_model_filters = self.get_extra_model_filters(request)
        return self.move_item(startorder, endorder, extra_model_filters)

    def move_item(self, startorder, endorder, extra_model_filters = None):
        model = self.model
        rank_field = self.default_order_field

        if endorder < startorder: # Drag up
            move_filter = {
                '{0}__gte'.format(rank_field): endorder,
                '{0}__lte'.format(rank_field): startorder - 1,
            }
            move_delta = +1
            order_by = '-{0}'.format(rank_field)
        elif endorder > startorder: # Drag down
            move_filter = {
                '{0}__gte'.format(rank_field): startorder + 1,
                '{0}__lte'.format(rank_field): endorder,
            }
            move_delta = -1
            order_by = rank_field
        else:
            return model.objects.none()

        obj_filters = {rank_field: startorder}
        if extra_model_filters is not None:
            obj_filters.update(extra_model_filters)
            move_filter.update(extra_model_filters)

        with transaction.atomic():
            try:
                obj = model.objects.get(**obj_filters)
            except model.MultipleObjectsReturned:
                msg = "Detected non-unique values in field '{0}' used for sorting this model.\nConsider to run \n"\
                      "    python manage.py reorder {1}\n"\
                      "to adjust this inconsistency."
                # noinspection PyProtectedMember
                raise model.MultipleObjectsReturned(msg.format(rank_field, model._meta.label))

            move_qs = model.objects.filter(**move_filter).order_by(order_by)
            move_objs = list(move_qs)
            for instance in move_objs:
                setattr(instance, rank_field, getattr(instance, rank_field) + move_delta)
                # Do not run `instance.save()`, because it will be updated later in bulk by `move_qs.update`.
                pre_save.send(
                    model,
                    instance=instance,
                    update_fields=[rank_field],
                    raw=False,
                    using=router.db_for_write(model, instance=instance),
                )
            move_qs.update(**{rank_field: F(rank_field) + move_delta})
            for instance in move_objs:
                post_save.send(
                    model,
                    instance=instance,
                    update_fields=[rank_field],
                    raw=False,
                    using=router.db_for_write(model, instance=instance),
                    created=False,
                )

            setattr(obj, rank_field, endorder)
            obj.save(update_fields=[rank_field])

        return [{'pk': instance.pk, 'order': getattr(instance, rank_field)} for instance in chain(move_objs, [obj])]

    def get_extra_model_filters(self, request):
        """
        Returns additional fields to filter sortable objects
        """
        return {}

    def get_max_order(self, request, obj=None):
        return self.model.objects.aggregate(max_order=Coalesce(Max(self.default_order_field), 0))['max_order']

    def _bulk_move(self, request, queryset, method):
        if not self.enable_sorting:
            return
        objects = self.model.objects.order_by(self.order_by)
        paginator = self.paginator(objects, self.list_per_page)
        current_page_number = int(request.GET.get('p', 0)) + 1

        if method == self.EXACT:
            page_number = int(request.POST.get('page', current_page_number))
            target_page_number = page_number
        elif method == self.BACK:
            step = int(request.POST.get('step', 1))
            target_page_number = current_page_number - step
        elif method == self.FORWARD:
            step = int(request.POST.get('step', 1))
            target_page_number = current_page_number + step
        elif method == self.FIRST:
            target_page_number = 1
        elif method == self.LAST:
            target_page_number = paginator.num_pages
        else:
            raise Exception('Invalid method')

        if target_page_number == current_page_number:
            # If you want the selected items to be moved to the start of the current page, then just do not return here.
            return

        try:
            page = paginator.page(target_page_number)
        except EmptyPage as ex:
            self.message_user(request, str(ex), level=messages.ERROR)
            return

        queryset_size = queryset.count()
        page_size = page.end_index() - page.start_index() + 1
        if queryset_size > page_size:
            msg = _("The target page size is {}. It is too small for {} items.").format(page_size, queryset_size)
            self.message_user(request, msg, level=messages.ERROR)
            return

        endorders_start = getattr(objects[page.start_index() - 1], self.default_order_field)
        endorders_step = -1 if self.order_by.startswith('-') else 1
        endorders = range(endorders_start, endorders_start + endorders_step * queryset_size, endorders_step)

        if page.number > current_page_number:  # Move forward (like drag down)
            queryset = queryset.reverse()
            endorders = reversed(endorders)

        for obj, endorder in zip(queryset, endorders):
            startorder = getattr(obj, self.default_order_field)
            self._move_item(request, startorder, endorder)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['sortable_update_url'] = self.get_update_url(request)
        extra_context['default_order_direction'] = self.default_order_direction
        return super(SortableAdminMixin, self).changelist_view(request, extra_context)

    def get_update_url(self, request):
        """
        Returns a callback URL used for updating items via AJAX drag-n-drop
        """
        return reverse('{}:{}'.format(self.admin_site.name, self._get_update_url_name()))


class PolymorphicSortableAdminMixin(SortableAdminMixin):
    """
    If the admin class is used for a polymorphic model, hence inherits from
    ``PolymorphicParentModelAdmin`` rather than ``admin.ModelAdmin``, then
    additionally inherit from ``PolymorphicSortableAdminMixin`` rather than
    ``SortableAdminMixin``.
    """
    def get_max_order(self, request, obj=None):
        return self.base_model.objects.aggregate(max_order=Coalesce(Max(self.default_order_field), 0))['max_order']


class CustomInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.default_order_direction, self.default_order_field = _get_default_ordering(self.model, self)

        if self.default_order_field not in self.form.base_fields:
            self.form.base_fields[self.default_order_field] = self.model._meta.get_field(self.default_order_field).formfield()

        self.form.base_fields[self.default_order_field].is_hidden = True
        self.form.base_fields[self.default_order_field].required = False
        self.form.base_fields[self.default_order_field].widget = widgets.HiddenInput()

        super(CustomInlineFormSet, self).__init__(*args, **kwargs)

    def save_new(self, form, commit=True):
        """
        New objects do not have a valid value in their ordering field. On object save, add an order
        bigger than all other order fields for the current parent_model.
        Strange behaviour when field has a default, this might be evaluated on new object and the value
        will be not None, but the default value.
        """
        obj = super(CustomInlineFormSet, self).save_new(form, commit=False)
        default_order_field = getattr(obj, self.default_order_field, None)
        if default_order_field is None or default_order_field >= 0:
            query_set = self.model.objects.filter(**{self.fk.get_attname(): self.instance.pk})
            max_order = query_set.aggregate(max_order=Coalesce(Max(self.default_order_field), 0))['max_order']
            setattr(obj, self.default_order_field, max_order + 1)
        if commit:
            obj.save()
        # form.save_m2m() can be called via the formset later on if commit=False
        if commit and hasattr(form, 'save_m2m'):
            form.save_m2m()
        return obj


class SortableInlineAdminMixin(SortableAdminBase):
    formset = CustomInlineFormSet

    def get_fields(self, request, obj=None):
        fields = super(SortableInlineAdminMixin, self).get_fields(request, obj)
        _, default_order_field = _get_default_ordering(self.model, self)
        fields = list(fields)

        if not (default_order_field in fields):
            # If the order field is not in the field list, add it
            fields.append(default_order_field)
        elif fields[0] == default_order_field:
            """
            Remove the order field and add it again immediately to ensure it is not on first position.
            This ensures that django's template for tabular inline renders the first column with colspan="2":

            ```
            {% for field in inline_admin_formset.fields %}
                {% if not field.widget.is_hidden %}
                    <th{% if forloop.first %} colspan="2"{% endif %}
            ```

            See https://github.com/jrief/django-admin-sortable2/issues/82
            """
            fields.append(fields.pop(0))

        return fields

    @property
    def media(self):
        shared = (
            super(SortableInlineAdminMixin, self).media
            + widgets.Media(js=('adminsortable2/js/libs/jquery.ui.sortable-1.11.4.js',
                                'adminsortable2/js/inline-sortable.js')))
        if isinstance(self, admin.StackedInline):
            return shared + widgets.Media(
                js=('adminsortable2/js/inline-sortable.js',
                    'adminsortable2/js/inline-stacked.js'))
        if isinstance(self, admin.TabularInline):
            return shared + widgets.Media(
                js=('adminsortable2/js/inline-sortable.js',
                    'adminsortable2/js/inline-tabular.js'))

    @property
    def template(self):
        if isinstance(self, admin.StackedInline):
            return 'adminsortable2/stacked.html'
        if isinstance(self, admin.TabularInline):
            return 'adminsortable2/tabular.html'
        raise ImproperlyConfigured('Class {0}.{1} must also derive from admin.TabularInline or admin.StackedInline'.format(self.__module__, self.__class__))
