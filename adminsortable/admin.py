#-*- coding: utf-8 -*-
import json
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage
from django.db import transaction
from django.db.models import Max, F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder


class SortableAdminMixin(object):
    class Media:
        css = {
            'all': ('adminsortable/css/sortable.css',)
        }
        js = ('cms' in settings.INSTALLED_APPS and (
            'cms/js/plugins/admincompat.js',
            'cms/js/libs/jquery.query.js',
            'cms/js/libs/jquery.ui.core.js',
            'cms/js/libs/jquery.ui.sortable.js',
        ) or (
            'adminsortable/js/plugins/admincompat.js',
            'adminsortable/js/libs/jquery.query.js',
            'adminsortable/js/libs/jquery.ui.core.js',
            'adminsortable/js/libs/jquery.ui.sortable.js',
        )) + ('adminsortable/js/sortable.js',)
    PREV = 0
    NEXT = 1
    FIRST = 2
    LAST = 3

    def __init__(self, model, admin_site):
        if not isinstance(getattr(model._meta, 'ordering', None), (list, tuple)):
            raise ImproperlyConfigured('Your model %s.%s contains no list "ordering" in its Meta class'
                % (model.__module__, model.__name__))
        self._default_ordering = model._meta.ordering[0]
        if not isinstance(getattr(self, 'exclude', None), (list, tuple)):
            self.exclude = [self._default_ordering]
        elif not self.exclude or self._default_ordering != self.exclude[0]:
            self.exclude = [self._default_ordering] + self.exclude
        if not getattr(self, 'change_list_template', None):
            self.change_list_template = 'adminsortable/change_list.html'
        super(SortableAdminMixin, self).__init__(model, admin_site)
        if not self.list_display_links:
            self.list_display_links = self.list_display[0]
        self.list_display = ['reorder'] + list(self.list_display)

    def get_urls(self):
        my_urls = patterns('',
            url(r'^adminsortable_update/$', self.admin_site.admin_view(self.update), name='sortable_update'),
        )
        return my_urls + super(SortableAdminMixin, self).get_urls()

    def get_changelist(self, request, **kwargs):
        order = self._get_order_direction(request)
        if not order or order == '1':
            self.enable_sorting = True
            self.order_by = self._default_ordering
        elif order == '-1':
            self.enable_sorting = True
            self.order_by = '-' + self._default_ordering
        else:
            self.enable_sorting = False
        if self.enable_sorting:
            self.actions += ['move_to_prev_page', 'move_to_next_page', 'move_to_first_page', 'move_to_last_page']
        return super(SortableAdminMixin, self).get_changelist(request, **kwargs)

    def reorder(self, item):
        html = ''
        if self.enable_sorting:
            html = '<div class="drag" order="%s">&nbsp;</div>' % item.order
        return html
    reorder.short_description = _('Sort')
    reorder.allow_tags = True
    reorder.admin_order_field = 'order'

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
            obj.order = self._max_order() + 1
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
                '%s__gte' % self._default_ordering: startorder,
                '%s__lte' % self._default_ordering: finalorder,
            }
            order_by = self._default_ordering
            move_update = { self._default_ordering: F(self._default_ordering) - 1 }
        elif startorder > endorder + order_down:
            finalorder = endorder + order_down
            move_filter = {
                '%s__gte' % self._default_ordering: finalorder,
                '%s__lte' % self._default_ordering: startorder,
            }
            order_by = '-' + self._default_ordering
            move_update = { self._default_ordering: F(self._default_ordering) + 1 }
        else:
            return self.model.objects.none()
        with transaction.commit_on_success():
            obj = self.model.objects.get(**{ self._default_ordering: startorder })
            setattr(obj, self._default_ordering, self._max_order() + 1)
            obj.save()
            self.model.objects.filter(**move_filter).order_by(order_by).update(**move_update)
            setattr(obj, self._default_ordering, finalorder)
            obj.save()
        return self.model.objects.filter(**move_filter).order_by(self._default_ordering).values('pk', self._default_ordering)

    def _max_order(self):
        max_order = self.model.objects.aggregate(max_order=Max(self._default_ordering))['max_order']
        return max_order if isinstance(max_order, (int, float, long)) else 0

    def _bulk_move(self, request, queryset, method):
        if not self.enable_sorting:
            return
        objects = self.model.objects.order_by(self.order_by)
        paginator = self.paginator(objects, self.list_per_page)
        page = paginator.page(int(request.REQUEST.get('p', 0)) + 1)
        try:
            if method == self.PREV:
                page = paginator.page(page.previous_page_number())
                endorder = getattr(objects[page.start_index() - 1], self._default_ordering)
                direction = +1
            elif method == self.NEXT:
                page = paginator.page(page.next_page_number())
                endorder = getattr(objects[page.start_index() - 1], self._default_ordering) + queryset.count()
                queryset = queryset.reverse()
                direction = -1
            elif method == self.FIRST:
                page = paginator.page(1)
                endorder = getattr(objects[page.start_index() - 1], self._default_ordering)
                direction = +1
            elif method == self.LAST:
                page = paginator.page(paginator.num_pages)
                endorder = getattr(objects[page.start_index() - 1], self._default_ordering) + queryset.count()
                queryset = queryset.reverse()
                direction = -1
            else:
                raise Exception('Invalid method')
        except EmptyPage:
            return
        endorder -= 1
        for obj in queryset:
            startorder = getattr(obj, self._default_ordering)
            self._move_item(request, startorder, endorder)
            endorder += direction
