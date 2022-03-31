from django.db import models


class Author(models.Model):
    name = models.CharField(
        "Name",
        null=True,
        blank=True,
        max_length=255,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SortableBook(models.Model):
    title = models.CharField(
        "Title",
        null=True,
        blank=True,
        max_length=255,
    )

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
    )

    author = models.ForeignKey(
        Author,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class SortableBook1(SortableBook):
    class Meta:
        proxy = True
        verbose_name = "Book"
        verbose_name_plural = "Books"


class SortableBook2(SortableBook):
    class Meta:
        proxy = True
        verbose_name = "Book"
        verbose_name_plural = "Books"


class SortableBook3(SortableBook):
    class Meta:
        proxy = True
        ordering = ['my_order']
        verbose_name = "Book"
        verbose_name_plural = "Books"


class SortableBook4(SortableBook):
    class Meta:
        proxy = True
        ordering = ['-my_order']
        verbose_name = "Book"
        verbose_name_plural = "Books"


class Chapter(models.Model):
    title = models.CharField(
        "Title",
        null=True,
        blank=True,
        max_length=255,
    )

    book = models.ForeignKey(
        SortableBook,
        null=True,
        on_delete=models.CASCADE,
    )

    my_order = models.PositiveIntegerField(
        blank=False,
        null=False,
        db_index=True,
    )

    class Meta:
        ordering = ['my_order']

    def __str__(self):
        return "Chapter: {0}".format(self.title)
