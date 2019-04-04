# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json

from types import MethodType

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage
try:
    from django.urls import reverse
except ImportError:  # Django<2.0
    from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.db.models import Max, F
from django.db.models.signals import post_save, pre_save
from django.forms.models import BaseInlineFormSet
from django.forms import widgets
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseForbidden)
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import admin

__all__ = ['SortableAdminMixin', 'SortableInlineAdminMixin']


def _get_default_ordering(model, model_admin):
    try:
        # first try with the model admin ordering
        none, prefix, field_name = model_admin.ordering[0].rpartition('-')
    except (AttributeError, IndexError, TypeError):
        pass
    else:
        return '{}1'.format(prefix), field_name

    try:
        # then try with the model ordering
        none, prefix, field_name = model._meta.ordering[0].rpartition('-')
    except (AttributeError, IndexError):
        msg = "Model {0}.{1} requires a list or tuple 'ordering' in its Meta class"
        raise ImproperlyConfigured(msg.format(model.__module__, model.__name__))

    return '{}1'.format(prefix), field_name


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
        css = {'all': ('adminsortable2/css/sortable.css',)}
        js = (
            'admin/js/jquery.init.js',
            'adminsortable2/js/plugins/admincompat.js',
            'adminsortable2/js/libs/jquery.ui.core-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.widget-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.mouse-1.11.4.js',
            'adminsortable2/js/libs/jquery.ui.sortable-1.11.4.js',
        )
        return super(SortableAdminBase, self).media + widgets.Media(css=css, js=js)


class SortableAdminMixin(SortableAdminBase):
    BACK, FORWARD, FIRST, LAST, EXACT = range(5)
    enable_sorting = False
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
        if not isinstance(self.exclude, (list, tuple)):
            self.exclude = [self.default_order_field]
        elif not self.exclude or self.default_order_field != self.exclude[0]:
            self.exclude = [self.default_order_field] + list(self.exclude)
        if not self.list_display_links:
            self.list_display_links = (self.list_display[0],)
        self._add_reorder_method()
        self.list_display = list(self.list_display)

        # Insert the magic field into the same position as the first occurrence
        # of the default_order_field, or, if not present, at the start
        try:
            self.list_display.insert(self.list_display.index(self.default_order_field), '_reorder')
        except ValueError:
            self.list_display.insert(0, '_reorder')

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
        order = self._get_order_direction(request)
        if order == '1':
            self.enable_sorting = True
            self.order_by = self.default_order_field
        elif order == '-1':
            self.enable_sorting = True
            self.order_by = '-' + self.default_order_field
        else:
            self.enable_sorting = False
        return super(SortableAdminMixin, self).get_changelist(request, **kwargs)

    @property
    def media(self):
        m = super(SortableAdminMixin, self).media
        if self.enable_sorting:
            m = m + widgets.Media(js=(
                'adminsortable2/js/libs/jquery.ui.sortable-1.11.4.js',
                'adminsortable2/js/list-sortable.js'))
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

    def _get_order_direction(self, request):
        return request.POST.get('o', request.GET.get('o', '1')).split('.')[0]

    def _move_item(self, request, startorder, endorder):
        if self._get_order_direction(request) != '-1':
            order_up, order_down = 0, 1
        else:
            order_up, order_down = 1, 0
        if startorder < endorder - order_up:
            finalorder = endorder - order_up
            move_filter = {
                '{0}__gte'.format(self.default_order_field): startorder,
                '{0}__lte'.format(self.default_order_field): finalorder,
            }
            order_by = self.default_order_field
            move_update = {self.default_order_field: F(self.default_order_field) - 1}
        elif startorder > endorder + order_down:
            finalorder = endorder + order_down
            move_filter = {
                '{0}__gte'.format(self.default_order_field): finalorder,
                '{0}__lte'.format(self.default_order_field): startorder,
            }
            order_by = '-{0}'.format(self.default_order_field)
            move_update = {self.default_order_field: F(self.default_order_field) + 1}
        else:
            return self.model.objects.none()
        with transaction.atomic():
            extra_model_filters = self.get_extra_model_filters(request)
            filters = {self.default_order_field: startorder}
            filters.update(extra_model_filters)
            move_filter.update(extra_model_filters)
            try:
                obj = self.model.objects.get(**filters)
            except self.model.MultipleObjectsReturned as exc:
                msg = "Detected non-unique values in field '{}' used for sorting this model.\nConsider to run \n"\
                      "    python manage.py reorder {}\n"\
                      "to adjust this inconsistency."
                raise self.model.MultipleObjectsReturned(msg.format(self.default_order_field, self.model._meta.label))
            obj_qs = self.model.objects.filter(pk=obj.pk)
            move_qs = self.model.objects.filter(**move_filter).order_by(order_by)
            for instance in move_qs:
                pre_save.send(
                    self.model,
                    instance=instance,
                    update_fields=[self.default_order_field],
                    raw=False,
                    using=None or router.db_for_write(
                        self.model,
                        instance=instance),
                )
            # using qs.update avoid multi [pre|post]_save signal on obj.save()
            obj_qs.update(**{self.default_order_field: self.get_max_order(request, obj) + 1})
            move_qs.update(**move_update)
            obj_qs.update(**{self.default_order_field: finalorder})
            for instance in move_qs:
                post_save.send(
                    self.model,
                    instance=instance,
                    update_fields=[self.default_order_field],
                    raw=False,
                    using=router.db_for_write(self.model, instance=instance),
                    created=False
                )
        query_set = self.model.objects.filter(**move_filter).order_by(self.default_order_field).values_list('pk', self.default_order_field)
        return [dict(pk=pk, order=order) for pk, order in query_set]

    def get_extra_model_filters(self, request):
        """
        Returns additional fields to filter sortable objects
        """
        return {}

    def get_max_order(self, request, obj=None):
        max_order = self.model.objects.aggregate(
            max_order=Max(self.default_order_field)
        )['max_order'] or 0
        return max_order

    def _bulk_move(self, request, queryset, method):
        if not self.enable_sorting:
            return
        objects = self.model.objects.order_by(self.order_by)
        paginator = self.paginator(objects, self.list_per_page)
        page = paginator.page(int(request.GET.get('p', 0)) + 1)
        step = int(request.POST.get('step', 1))
        try:
            if method == self.EXACT:
                target_page = int(request.POST.get('page', page))
                if page.number == target_page:
                    return
                elif target_page > page.number:
                    direction = -1
                else:
                    direction = +1
                page = paginator.page(target_page)
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field)
                if direction == -1:
                    endorder += queryset.count()
                    queryset = queryset.reverse()
            elif method == self.BACK:
                page = paginator.page(page.number - step)
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field)
                direction = +1
            elif method == self.FORWARD:
                page = paginator.page(page.number + step)
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field) + queryset.count()
                queryset = queryset.reverse()
                direction = -1
            elif method == self.FIRST:
                page = paginator.page(1)
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field)
                direction = +1
            elif method == self.LAST:
                page = paginator.page(paginator.num_pages)
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field) + queryset.count()
                queryset = queryset.reverse()
                direction = -1
            else:
                raise Exception('Invalid method')
        except EmptyPage:
            return
        endorder -= 1
        for obj in queryset:
            startorder = getattr(obj, self.default_order_field)
            self._move_item(request, startorder, endorder)
            endorder += direction

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
        return self.base_model.objects.aggregate(
            max_order=Max(self.default_order_field)
        )['max_order'] or 0


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
            max_order = query_set.aggregate(max_order=Max(self.default_order_field))['max_order'] or 0
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
