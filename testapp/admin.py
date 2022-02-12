from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from . import models

admin.site.enable_nav_sidebar = False


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(models.Notes)
class NoteAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['note']
    ordering = ['note']


class ChapterInline(SortableInlineAdminMixin, admin.StackedInline):
    model = models.Chapter
    extra = 1


class NotesInline(admin.TabularInline):
    model = models.Notes
    extra = 1


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 12
    list_display = ['author', 'title', 'my_order']
    list_display_links = ['title']
    inlines = [ChapterInline, NotesInline]


class UpOrderedSortableBookAdmin(SortableBookAdmin):
    ordering = ['my_order']


class DownOrderedSortableBookAdmin(SortableBookAdmin):
    ordering = ['-my_order']


admin.site.register(models.SortableBook1, UpOrderedSortableBookAdmin)
admin.site.register(models.SortableBook2, DownOrderedSortableBookAdmin)
admin.site.register(models.SortableBook3, SortableBookAdmin)
admin.site.register(models.SortableBook4, SortableBookAdmin)
