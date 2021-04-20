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

    class Meta(object):
        ordering = ['my_order']

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Chapter(models.Model):
    title = models.CharField('Title', null=True, blank=True, max_length=255)
    book = models.ForeignKey(SortableBook, null=True, on_delete=models.CASCADE)
    my_order = models.PositiveIntegerField(blank=False, null=False)

    class Meta(object):
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
