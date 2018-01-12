
from adminsortable2.admin import (CustomInlineFormSet, SortableAdminMixin,
                                  SortableInlineAdminMixin)
from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableStackedInline
from parler.forms import TranslatableBaseInlineFormSet
from parler_example.parler_test_app.models import Chapter, SortableBook


class TranslatableSortableInlineFormSet(CustomInlineFormSet, TranslatableBaseInlineFormSet):
    pass


class ChapterInline(TranslatableStackedInline, SortableInlineAdminMixin, admin.StackedInline):
    model = Chapter
    extra = 1

    formset = TranslatableSortableInlineFormSet

    @property
    def template(self):
        return "adminsortable2/stacked.html"


@admin.register(SortableBook)
class SortableBookAdmin(SortableAdminMixin, TranslatableAdmin):
    list_per_page = 12
    list_display = ("title",)
    list_display_links = ("title",)
    inlines = (ChapterInline,)
