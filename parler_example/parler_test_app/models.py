
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class SortableBook(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField('Title', null=True, blank=True, max_length=255)
    )
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ['my_order']

    def __str__(self):
        return self.safe_translation_getter(
            field="title",
            language_code=self.language_code,
            any_language=True
        ) or "no title"


class Chapter(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField('Title', null=True, blank=True, max_length=255)
    )
    book = models.ForeignKey(SortableBook, null=True, on_delete=models.CASCADE)
    my_order = models.PositiveIntegerField(blank=False, null=False)

    class Meta(object):
        ordering = ['my_order']

    def __str__(self):
        return self.safe_translation_getter(
            field="title",
            language_code=self.language_code,
            any_language=True
        ) or "no title"
