#-*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable.admin import SortableAdminMixin, SortableInlineAdminMixin
from models import Author, SortableBook, Chapter, Notes


class ChapterInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Chapter
    extra = 1


class NotesInline(admin.TabularInline):
    model = Notes
    extra = 1


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 8
    list_display = ('title', 'my_order',)
    inlines = (ChapterInline, NotesInline,)
admin.site.register(SortableBook, SortableBookAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Author, AuthorAdmin)
