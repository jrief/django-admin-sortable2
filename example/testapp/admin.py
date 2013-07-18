#-*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable.admin import SortableAdminMixin
from models import SortableBook


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 15
admin.site.register(SortableBook, SortableBookAdmin)
