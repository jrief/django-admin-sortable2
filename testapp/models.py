from django.db import models


class Author(models.Model):
    name = models.CharField('Name', null=True, blank=True, max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class SortableBook(models.Model):
    title = models.CharField('Title', null=True, blank=True, max_length=255)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    author = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class SortableBook1(SortableBook):
    class Meta:
        proxy = True
        verbose_name = "Book 1"
        verbose_name_plural = "Books 1"


class SortableBook2(SortableBook):
    class Meta:
        proxy = True
        verbose_name = "Book 2"
        verbose_name_plural = "Books 2"


class SortableBook3(SortableBook):
    class Meta:
        proxy = True
        ordering = ['my_order']
        verbose_name = "Book 3"
        verbose_name_plural = "Books 3"


class SortableBook4(SortableBook):
    class Meta:
        proxy = True
        ordering = ['-my_order']
        verbose_name = "Book 4"
        verbose_name_plural = "Books 4"


class Chapter(models.Model):
    title = models.CharField('Title', null=True, blank=True, max_length=255)
    book = models.ForeignKey(SortableBook, null=True, on_delete=models.CASCADE)
    my_order = models.PositiveIntegerField(blank=False, null=False, db_index=True)

    class Meta:
        ordering = ['my_order']

    def __str__(self):
        return 'Chapter: {0}'.format(self.title)

    def __unicode__(self):
        return 'Chapter: {0}'.format(self.title)


class Notes(models.Model):
    note = models.CharField('Note', null=True, blank=True, max_length=255)
    book = models.ForeignKey(SortableBook, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'Note: {0}'.format(self.note)

    def __unicode__(self):
        return 'Note: {0}'.format(self.note)
