from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from . import models

admin.site.enable_nav_sidebar = False


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']


class ChapterStackedInline(SortableInlineAdminMixin, admin.StackedInline):
    model = models.Chapter
    extra = 1


class ChapterStackedInlineReversed(SortableInlineAdminMixin, admin.StackedInline):
    model = models.Chapter
    extra = 1
    ordering = ['-my_order']


class ChapterTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = models.Chapter
    extra = 1


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 12
    list_display = ['title', 'author', 'my_order']


class UpOrderedSortableBookAdmin(SortableBookAdmin):
    inlines = [ChapterStackedInline]
    ordering = ['my_order']


class DownOrderedSortableBookAdmin(SortableBookAdmin):
    inlines = [ChapterStackedInlineReversed]
    ordering = ['-my_order']


class UnorderedSortableBookAdmin(SortableBookAdmin):
    inlines = [ChapterTabularInline]


class OrderedSortableBookAdmin(SortableBookAdmin):
    ordering = ['my_order']


admin.site.register(models.SortableBook, OrderedSortableBookAdmin)
admin.site.register(models.SortableBook1, UpOrderedSortableBookAdmin)
admin.site.register(models.SortableBook2, DownOrderedSortableBookAdmin)
admin.site.register(models.SortableBook3, UnorderedSortableBookAdmin)
admin.site.register(models.SortableBook4, UnorderedSortableBookAdmin)
