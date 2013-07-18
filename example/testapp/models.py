# -*- coding: utf-8 -*-
from django.db import models


class SortableBook(models.Model):
    title = models.CharField('Title', null=True, blank=True, max_length=255)
    order = models.PositiveIntegerField(blank=True, unique=True)

    class Meta(object):
        ordering = ['order']

    def __unicode__(self):
        return self.title
