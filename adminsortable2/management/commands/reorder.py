# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import inspect
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.contrib.admin import site
from ...admin import SortableAdminMixin


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Restore the primary ordering fields of a model containing a special ordering field'

    def add_arguments(self, parser):
        parser.add_argument('models or apps', nargs='+', type=str)

    def handle(self, *args, **options):
        def set_order_model_objects(model):
            """Set order to model's all objects"""
            if not hasattr(model._meta, 'ordering') or len(model._meta.ordering) == 0:
                raise CommandError(
                    'Model "{0}" does not define field "ordering" in its Meta class'.format(
                        model_or_app_name))
            orderfield = model._meta.ordering[0]
            if orderfield[0] == '-':
                orderfield = orderfield[1:]
            for order, obj in enumerate(model.objects.iterator(), start=1):
                setattr(obj, orderfield, order)
                obj.save()
            self.stdout.write('Successfully reordered model "{0}"'.format(model))

        for model_or_app_name in options['models or apps']:
            try:
                app_label, model_name = model_or_app_name.rsplit('.', 1)
                model = apps.get_model(app_label, model_name)
            # if the attempt to split fails, the app with that name gets the sortable models
            except ValueError:
                try:
                    # Check the app is exist
                    apps.get_app_config(model_or_app_name)
                    # Import registered Models and ModelAdmins in _registry of admin app.
                    for model, model_admin in site._registry.items():
                        # Check current model is current app's model
                        if str(model_admin).startswith('%s.' % model_or_app_name):
                            # If ModelAdmin inherits SortableAdminMixin,
                            # use the Model to execute the set_order_model_objects () method.
                            if SortableAdminMixin in inspect.getmro(model_admin.__class__):
                                set_order_model_objects(model)
                except:
                    raise CommandError('Unable to load app "%s"' % model_or_app_name)
            except ImportError:
                raise CommandError('Unable to load model "%s"' % model_or_app_name)
            else:
                set_order_model_objects(model)
