#-*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable.admin import SortableAdminMixin
from models import Author, SortableBook


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 15
    list_display = ('title', 'order',)
admin.site.register(SortableBook, SortableBookAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Author, AuthorAdmin)
