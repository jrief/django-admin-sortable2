# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_by_path
from django.core import exceptions


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Restore the primary ordering fields of a model containing a special ordering field'

    def handle(self, *args, **options):
        for modelname in args:
            try:
                Model = import_by_path(modelname)
            except exceptions.ImproperlyConfigured:
                raise CommandError('Unable to load model "%s"' % modelname)
            if not hasattr(Model._meta, 'ordering') or len(Model._meta.ordering) == 0:
                raise CommandError('Model "{0}" does not define field "ordering" in its Meta class'.format(modelname))
            orderfield = Model._meta.ordering[0]
            order = 0
            for obj in Model.objects.all():
                order += 1
                setattr(obj, orderfield, order)
                obj.save()
            self.stdout.write('Successfully reordered model "{0}"'.format(modelname))
