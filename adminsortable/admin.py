# -*- coding: utf-8 -*-
import json
from types import MethodType
from django import VERSION
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage
from django.db import transaction
from django.db.models import Max, F
from django.forms.models import BaseInlineFormSet
from django.forms.widgets import HiddenInput
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import admin


class SortableAdminBase(object):
    class Media:
        css = {'all': ('adminsortable/css/sortable.css',)}
        if VERSION[0] == 1 and VERSION[1] <= 5:
            js = (
                'adminsortable/js/plugins/admincompat.js',
                'adminsortable/js/libs/jquery.ui.core-1.7.1.js',
                'adminsortable/js/libs/jquery.ui.sortable-1.7.1.js',
            )
        else:
            js = (
                'adminsortable/js/plugins/admincompat.js',
                'adminsortable/js/libs/jquery.ui.core-1.10.3.js',
                'adminsortable/js/libs/jquery.ui.widget-1.10.3.js',
                'adminsortable/js/libs/jquery.ui.mouse-1.10.3.js',
                'adminsortable/js/libs/jquery.ui.sortable-1.10.3.js',
            )
        if 'cms' in settings.INSTALLED_APPS:
            try:
                # for DjangoCMS < 3, override jQuery files for inclusion from the CMS
                from cms import __version__
                cms_version = __version__.split('.')
                if int(cms_version[0]) < 3:
                    js = (
                        'cms/js/plugins/admincompat.js',
                        'cms/js/libs/jquery.query.js',
                        'cms/js/libs/jquery.ui.core.js',
                        'cms/js/libs/jquery.ui.sortable.js',
                    )
            except ImportError:
                # other packages may pollute the import search path with 'cms'
                pass

    def order_field_verbose_name(self):

        model = self.model
        try:
            default_order_field = self.model._meta.ordering[0].lstrip('-')
        except (AttributeError, IndexError):
            raise ImproperlyConfigured('Model {0}.{1} requires a list or tuple "ordering" in its Meta class'.format(model.__module__, model.__name__))

        return model._meta.get_field_by_name(default_order_field)[0].verbose_name


class SortableAdminMixin(SortableAdminBase):
    PREV, NEXT, FIRST, LAST = range(4)

    def __init__(self, model, admin_site):
        try:
            self.default_order_field = model._meta.ordering[0].lstrip('-')
        except (AttributeError, IndexError):
            raise ImproperlyConfigured('Model {0}.{1} requires a list or tuple "ordering" in its Meta class'.format(model.__module__, model.__name__))
        super(SortableAdminMixin, self).__init__(model, admin_site)
        if not isinstance(getattr(self, 'exclude', None), (list, tuple)):
            self.exclude = [self.default_order_field]
        elif not self.exclude or self.default_order_field != self.exclude[0]:
            self.exclude = [self.default_order_field] + self.exclude
        if not getattr(self, 'change_list_template', None):
            self.change_list_template = 'adminsortable/change_list.html'
        if not self.list_display_links:
            self.list_display_links = self.list_display[0]
        self._add_reorder_method()
        self.list_display = ['_reorder'] + list(self.list_display)

    def get_urls(self):
        my_urls = patterns('',
            url(r'^adminsortable_update/$', self.admin_site.admin_view(self.update), name='sortable_update'),
        )
        return my_urls + super(SortableAdminMixin, self).get_urls()

    def get_actions(self, request):
        actions = super(SortableAdminMixin, self).get_actions(request)
        paginator = self.get_paginator(request, self.queryset(request), self.list_per_page)
        if len(paginator.page_range) > 1:
            # add actions for moving items to other pages
            move_actions = []
            cur_page = int(request.REQUEST.get('p', 0)) + 1
            if len(paginator.page_range) > 2 and cur_page > paginator.page_range[1]:
                move_actions.append('move_to_first_page')
            if cur_page > paginator.page_range[0]:
                move_actions.append('move_to_prev_page')
            if cur_page < paginator.page_range[-1]:
                move_actions.append('move_to_next_page')
            if len(paginator.page_range) > 2 and cur_page < paginator.page_range[-2]:
                move_actions.append('move_to_last_page')
            for fname in move_actions:
                actions.update({fname: self.get_action(fname)})
        return actions

    def get_changelist(self, request, **kwargs):
        order = self._get_order_direction(request)
        if not order or order == '1':
            self.enable_sorting = True
            self.order_by = self.default_order_field
        elif order == '-1':
            self.enable_sorting = True
            self.order_by = '-' + self.default_order_field
        else:
            self.enable_sorting = False
        if self.enable_sorting:
            try:
                self.Media.js += ('adminsortable/js/list-sortable.js',)
            except AttributeError:
                self.Media.js = ('adminsortable/js/list-sortable.js',)
        return super(SortableAdminMixin, self).get_changelist(request, **kwargs)

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
                html = '<div class="drag" order="{0}">&nbsp;</div>'.format(getattr(item, this.default_order_field))
            return html

        setattr(func, 'allow_tags', True)
        setattr(func, 'short_description', self.order_field_verbose_name())
        setattr(func, 'admin_order_field', self.default_order_field)
        setattr(self, '_reorder', MethodType(func, self))

    @csrf_exempt
    def update(self, request):
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
            setattr(obj, self.default_order_field, self.get_max_order() + 1)
        obj.save()

    def move_to_prev_page(self, request, queryset):
        self._bulk_move(request, queryset, self.PREV)
    move_to_prev_page.short_description = _('Move selected to previous page')

    def move_to_next_page(self, request, queryset):
        self._bulk_move(request, queryset, self.NEXT)
    move_to_next_page.short_description = _('Move selected to next page')

    def move_to_first_page(self, request, queryset):
        self._bulk_move(request, queryset, self.FIRST)
    move_to_first_page.short_description = _('Move selected to first page')

    def move_to_last_page(self, request, queryset):
        self._bulk_move(request, queryset, self.LAST)
    move_to_last_page.short_description = _('Move selected to last page')

    def _get_order_direction(self, request):
        return request.REQUEST.get('o', '').split('.')[0]

    def _move_item(self, request, startorder, endorder):
        if self._get_order_direction(request) != '-1':
            order_up, order_down = 0, 1
        else:
            order_up, order_down = 1, 0
        if startorder < endorder - order_up:
            finalorder = endorder - order_up
            move_filter = {
                '%s__gte' % self.default_order_field: startorder,
                '%s__lte' % self.default_order_field: finalorder,
            }
            order_by = self.default_order_field
            move_update = {self.default_order_field: F(self.default_order_field) - 1}
        elif startorder > endorder + order_down:
            finalorder = endorder + order_down
            move_filter = {
                '%s__gte' % self.default_order_field: finalorder,
                '%s__lte' % self.default_order_field: startorder,
            }
            order_by = '-' + self.default_order_field
            move_update = {self.default_order_field: F(self.default_order_field) + 1}
        else:
            return self.model.objects.none()
        with transaction.commit_on_success():
            obj = self.model.objects.get(**{self.default_order_field: startorder})
            setattr(obj, self.default_order_field, self.get_max_order() + 1)
            obj.save()
            self.model.objects.filter(**move_filter).order_by(order_by).update(**move_update)
            setattr(obj, self.default_order_field, finalorder)
            obj.save()
        query_set = self.model.objects.filter(**move_filter).order_by(self.default_order_field).values_list('pk', self.default_order_field)
        return [dict(pk=pk, order=order) for pk, order in query_set]

    def get_max_order(self):
        max_order = self.model.objects.aggregate(max_order=Max(self.default_order_field))['max_order'] or 0
        return max_order

    def _bulk_move(self, request, queryset, method):
        if not self.enable_sorting:
            return
        objects = self.model.objects.order_by(self.order_by)
        paginator = self.paginator(objects, self.list_per_page)
        page = paginator.page(int(request.REQUEST.get('p', 0)) + 1)
        try:
            if method == self.PREV:
                page = paginator.page(page.previous_page_number())
                endorder = getattr(objects[page.start_index() - 1], self.default_order_field)
                direction = +1
            elif method == self.NEXT:
                page = paginator.page(page.next_page_number())
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


class CustomInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        try:
            self.default_order_field = self.model._meta.ordering[0]
        except (AttributeError, IndexError):
            raise ImproperlyConfigured('Model {0}.{1} requires a list or tuple "ordering" in its Meta class'.format(self.model.__module__, self.model.__name__))
        self.form.base_fields[self.default_order_field].is_hidden = True
        self.form.base_fields[self.default_order_field].required = False
        self.form.base_fields[self.default_order_field].widget = HiddenInput()
        super(CustomInlineFormSet, self).__init__(*args, **kwargs)

    def save_new(self, form, commit=True):
        """
        New objects do not have a valid value in their ordering field. On object save, add an order
        bigger than all other order fields for the current parent_model.
        """
        obj = super(CustomInlineFormSet, self).save_new(form, commit=False)
        if getattr(obj, self.default_order_field, None) is None:
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

    def __init__(self, parent_model, admin_site):
        version = (VERSION[0] == 1 and VERSION[1] <= 5) and '1.5' or '1.6'
        if isinstance(self, admin.StackedInline):
            self.template = 'adminsortable/stacked-%s.html' % version
            self.Media.js += ('adminsortable/js/inline-sortable.js',)
        elif isinstance(self, admin.TabularInline):
            self.template = 'adminsortable/tabular-%s.html' % version
            self.Media.js += ('adminsortable/js/inline-sortable.js',)
        else:
            raise ImproperlyConfigured('Class {0}.{1} must also derive from admin.TabularInline or admin.StackedInline'.format(self.__module__, self.__class__))
        self.Media.css['all'] += ('adminsortable/css/sortable.css',)
        super(SortableInlineAdminMixin, self).__init__(parent_model, admin_site)
