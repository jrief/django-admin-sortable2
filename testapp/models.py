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


class Book(models.Model):
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

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"


# class SortableBook2(SortableBook):
#     class Meta:
#         proxy = True
#         verbose_name = "Book"
#         verbose_name_plural = "Books (reverse ordered by admin)"


class Book1(Book):
    class Meta:
        proxy = True
        ordering = ['my_order']
        verbose_name = "Book"
        verbose_name_plural = "Books (ordered by model, no inlines)"


class Book2(Book):
    class Meta:
        proxy = True
        ordering = ['-my_order']
        verbose_name = "Book"
        verbose_name_plural="Books (reverse ordered by model, no inlines)"

# class SortableBook5(SortableBook):
#     class Meta:
#         proxy = True
#         verbose_name = "Book"
#         verbose_name_plural = "Books (unsorted)"
#
#
# class SortableBookA(SortableBook):
#     class Meta:
#         proxy = True
#         verbose_name = "Book"
#         verbose_name_plural = "Books (extra admin mixin)"


class Chapter(models.Model):
    title = models.CharField(
        "Title",
        null=True,
        blank=True,
        max_length=255,
    )

    book = models.ForeignKey(
        Book,
        null=True,
        on_delete=models.CASCADE,
    )

    my_order = models.PositiveIntegerField(
        blank=False,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return "Chapter: {0}".format(self.title)


class Chapter1(Chapter):
    class Meta:
        proxy = True
        ordering = ['my_order']


class Chapter2(Chapter):
    class Meta:
        proxy = True
        ordering = ['-my_order']
