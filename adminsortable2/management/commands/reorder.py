# -*- coding: utf-8 -*-
import django
from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions

if django.VERSION[:2] < (1, 7):
    from django.utils.module_loading import import_by_path as import_string
else:
    from django.utils.module_loading import import_string


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Restore the primary ordering fields of a model containing a special ordering field'

    def handle(self, *args, **options):
        for modelname in args:
            try:
                Model = import_string(modelname)
            except exceptions.ImproperlyConfigured:
                raise CommandError('Unable to load model "%s"' % modelname)
            if not hasattr(Model._meta, 'ordering') or len(Model._meta.ordering) == 0:
                raise CommandError('Model "{0}" does not define field "ordering" in its Meta class'.format(modelname))
            orderfield = Model._meta.ordering[0]
            for order, obj in enumerate(Model.objects.iterator(), start=1):
                setattr(obj, orderfield, order)
                obj.save()
            self.stdout.write('Successfully reordered model "{0}"'.format(modelname))
