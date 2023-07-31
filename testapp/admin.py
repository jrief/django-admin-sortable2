from django.contrib import admin

from adminsortable2.admin import SortableAdminBase, SortableAdminMixin, SortableInlineAdminMixin, SortableStackedInline, SortableTabularInline

from testapp.models import Author, Chapter, Chapter1, Chapter2, Book, Book1, Book2


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']


class ChapterStackedInline(SortableStackedInline):
    model = Chapter1  # model is ordered
    extra = 1


class ChapterStackedInlineReversed(SortableStackedInline):
    model = Chapter2  # model is reverse ordered
    extra = 1


class ChapterStackedInlineUpOrdered(SortableInlineAdminMixin, admin.StackedInline):
    model = Chapter
    extra = 1
    ordering = ['my_order']


class ChapterStackedInlineDownOrdered(SortableInlineAdminMixin, admin.StackedInline):
    model = Chapter
    extra = 1
    ordering = ['-my_order']


class ChapterTabularInline(SortableTabularInline):
    model = Chapter
    extra = 1
    ordering = ['my_order']


class SortableBookAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_per_page = 12
    list_display = ['title', 'author', 'my_order']


class UpOrderedSortableBookAdmin(SortableBookAdmin):
    inlines = [ChapterStackedInlineUpOrdered]
    ordering = ['my_order']


class DownOrderedSortableBookAdmin(SortableBookAdmin):
    inlines = [ChapterStackedInlineDownOrdered]
    ordering = ['-my_order']


class SortableBookAdminStacked(SortableBookAdmin):
    inlines = [ChapterStackedInline]


class SortableBookAdminStackedReversed(SortableBookAdmin):
    inlines = [ChapterStackedInlineReversed]


class SortableBookAdminTabular(SortableBookAdmin):
    inlines = [ChapterTabularInline]
    ordering = ['my_order']


class UnsortedBookAdmin(SortableAdminBase, admin.ModelAdmin):
    """
    Test if SortableInlineAdminMixin works without sorted parent model:
    Here Chapter is sorted, but Book is not.
    """
    list_per_page = 12
    list_display = ['title', 'author']
    inlines = [ChapterStackedInline]


class ImportExportMixin:
    """
    Dummy mixin class to test if a proprietary change_list_template is properly overwritten.
    """
    change_list_template = 'testapp/impexp_change_list.html'


class SortableAdminExtraMixin(SortableAdminMixin, ImportExportMixin, admin.ModelAdmin):
    """
    Test if SortableAdminMixin works if admin class inherits from extra mixins overriding
    the change_list_template template.
    """
    list_per_page = 12
    ordering = ['my_order']
    inlines = [ChapterStackedInline]


class BookAdminSite(admin.AdminSite):
    enable_nav_sidebar = False

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Register the given model(s) with the given admin class.
        Allows to register a model more than one time.
        """
        if not issubclass(model_or_iterable, Book):
            return super().register(model_or_iterable, admin_class, **options)

        model = model_or_iterable

        class Meta:
            proxy = True

        verbose_name_plural = options.pop('name', model._meta.verbose_name_plural)
        attrs = {'Meta': Meta, '__module__': model.__module__}
        infix = options.pop('infix', '')
        name = f'Book{infix}'
        model = type(name, (model,), attrs)
        model._meta.verbose_name_plural = verbose_name_plural

        assert model not in self._registry
        self._registry[model] = admin_class(model, self)

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        for app in app_list:
            if app_label == 'testapp':
                app['models'].sort(key=lambda x: x['admin_url'])
            else:
                app['models'].sort(key=lambda x: x['name'])
        return app_list


admin.site = BookAdminSite()
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book1, SortableBookAdmin, infix=0)
admin.site.register(Book1, SortableBookAdminStacked, name="Books (ordered by model, stacked inlines)", infix=1)
admin.site.register(Book2, SortableBookAdminStackedReversed, name="Books (reverse ordered by model, stacked inlines)", infix=2)
admin.site.register(Book, UpOrderedSortableBookAdmin, name="Books (ordered by admin, stacked inlines)", infix=3)
admin.site.register(Book, DownOrderedSortableBookAdmin, name="Books (reverse ordered by admin, stacked inlines)", infix=4)
admin.site.register(Book, SortableBookAdminTabular, name="Books (ordered by admin, tabular inlines)", infix=5)
admin.site.register(Book, UnsortedBookAdmin, name="Unsorted Books (sorted stacked inlines)", infix=6)
admin.site.register(Book, SortableAdminExtraMixin, name="Books (inheriting from external admin mixin)", infix=7)
