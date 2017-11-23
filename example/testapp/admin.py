#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from . import models


class ChapterInline(SortableInlineAdminMixin, admin.StackedInline):
    model = models.Chapter
    extra = 1


class NotesInline(admin.TabularInline):
    model = models.Notes
    extra = 1


@admin.register(models.SortableBook)
class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 12
    list_display = ('author', 'title', 'my_order',)
    list_display_links = ('title',)
    inlines = (ChapterInline, NotesInline,)


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.Notes)
class NoteAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('note',)
    ordering = ('note',)
