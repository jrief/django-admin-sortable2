#-*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable.admin import SortableAdminMixin, SortableInlineAdminMixin
from models import Author, SortableBook, Chapter


class ChapterInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Chapter
    extra = 1


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 15
    list_display = ('title', 'my_order',)
    inlines = (ChapterInline,)
admin.site.register(SortableBook, SortableBookAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Author, AuthorAdmin)
