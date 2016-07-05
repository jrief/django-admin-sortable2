.. _usage:

====================
Using Admin Sortable
====================

This Django module offers three mixin classes to be added to the existing classes of your model
admin:

* ``admin.ModelAdmin``
* ``admin.StackedInline``
* ``admin.TabularInline``

They slightly modify the admin views of a sortable model. There is no need to derive your model
class from a special base model class. You can use your existing ordered field, just as you always
did, or add a new one with any name you like, if needed.


Integrate your models
=====================

Each database model which shall be sortable, requires a position value in its model description.
Rather than defining a base class, which contains such a positional value in a hard coded field,
this module lets you reuse existing sort fields or define a new field for the sort value.

Therefore this module can be applied in situations where your model is derived from an existing
abstract model which already contains any kind of position value. The only requirement for this
module is, that this position value be specified as the primary field used for sorting. This
in Django is declared through the model's Meta class. An example ``models.py``:

.. code:: python

	class SortableBook(models.Model):
	    title = models.CharField('Title', null=True, blank=True, max_length=255)
	    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)
	
	    class Meta(object):
	        ordering = ('my_order',)

Here the ordering field is named ``my_order``, but you may choose any other name. There are three
constraints:

* ``my_order`` is the first field in the ``ordering`` tuple of the model's Meta class.
* ``my_order``'s default value must be 0. The JavaScript which performs the sorting is 1-indexed,
	so this will not interfere with the order of your items, even if you're already using 0-indexed
	ordering fields.
* The ``my_order`` field must be editable, so make sure that you **do not** add ``editable=False`` to it.

The field used to store the ordering position may be any kind of numeric model field offered by
Django. Use one of these models fields:

* ``models.BigIntegerField``
* ``models.IntegerField``
* ``models.PositiveIntegerField`` (recommended)
* ``models.PositiveSmallIntegerField`` (recommended for small sets)
* ``models.SmallIntegerField``

Additionally you may use ``models.DecimalField`` or ``models.FloatField``, but these model fields
are not recommended.

.. warning:: Do not make this field unique! See below why.


In Django's Admin, make the list view sortable
==============================================

Next to the action checkbox, a draggable area is added to each entry line. The user than may click
on any item and vertically drag that item to a new position.

.. figure:: _static/list-view.png
   :alt: Sortable List View


Sortable List View
------------------

If one or more items shall be moved to another page, this can easily been done by selecting them
though the action checkbox. Then the user shall click on a predefined action from the pull down
menu on the top of the list view.


Integrate into a list view
..........................

In ``admin.py``, add a mixin class to augment the functionality for sorting (be sure to put the
mixin class before model.ModelAdmin):

.. code:: python

	from django.contrib import admin
	from adminsortable2.admin import SortableAdminMixin
	from models import MyModel
	
	class MyModelAdmin(SortableAdminMixin, admin.ModelAdmin):
	    pass
	admin.site.register(MyModel, MyModelAdmin)

That's it! The list view of the model admin interface now adds a column with a sensitive area.
By clicking on that area, the user can move that row up or down. If he wants to move it to another
page, he can do that as a bulk operation, using the admin actions.

**Note**: If you're modifying the available fields, the ordering field must be included. This applies to stacked or tabular inlines too.

.. code:: python

	class MyModelAdmin(SortableAdminMixin, admin.ModelAdmin):
	    fields = ('my_order', ...)
	    pass


Overriding change list page
...........................

To add for example a custom tool to the change list view, copy ``contrib/admin/templates/admin/change_list.html``
to either ``templates/admin/my_app/`` or ``templates/admin/my_app/page/`` directory of your project and make sure
you are extending from the right template:

.. code:: html

    {% extends "adminsortable2/change_list.html" %}

    {% block object-tools-items %}
        {{ block.super }}
        <li>
            <a href="mylink/">My Link</a>
        </li>
    {% endblock %}


Make a stacked or tabular inline view sortable
==============================================

The interface for a sortable stacked inline view looks exactly the same. If you click on an stacked
inline's field title, this whole inline form can be moved up and down.

The interface for a sortable tabular inline view adds a sensitive area to each draggable row. These
rows then can be moved up and down.

.. figure:: _static/tabular-inline.png
   :alt: Sortable Tabular Inlines


Sortable Tabular Inlines
------------------------

After moving a tabular or stacked inline, save the model form to persist
its sorting order.


Integrate into a detail view
............................

.. code:: python

	from django.contrib import admin
	from adminsortable2.admin import SortableInlineAdminMixin
	from models import MySubModel, MyModel
	
	class MySubModelInline(SortableInlineAdminMixin, admin.TabularInline):  # or admin.StackedInline
	    model = MySubModel
	
	class MyModelAdmin(admin.ModelAdmin):
	    inlines = (MySubModelInline,)
	admin.site.register(MyModel, MyModelAdmin)


Initial data
============

In case you just changed your model to contain an additional sorting
field (e.g. ``my_order``), which does not yet contain any values, then
you **must** set initial ordering values.

**django-admin-sortable2** is shipping with a management command which can be used to prepopulate
the ordering field:

.. code:: python

	shell> ./manage.py reorder my_app.models.MyModel

If you prefer to do a one-time database migration, just after having added the ordering field 
to the model, then create a datamigration. For Django < 1.6, using South:

.. code:: python

	shell> ./manage.py datamigration myapp preset_order

this creates an empty migration named something like ``migrations/0123_preset_order.py``. Edit the
file and change it into a data migration:

.. code:: python

	class Migration(DataMigration):
	    def forwards(self, orm):
	        for order, obj in enumerate(orm.MyModel.objects.iterator(), start=1):
	            obj.my_order = order
	            obj.save()

And for Django 1.6 and up above:

..code:: python

	shell> ./manage.py makemigrations myapp

this creates **non** empty migration named somethin like ``migrations/0123_auto_20160208_054.py``.

Edit the
file and change it into a data migration:

.. code:: python

	def reorder(apps, schema_editor):
	    MyModel = apps.get_model("myapp", "MyModel")
	    order = 0
	    for item in MyModel.objects.all():
	        order += 1
	        item.my_order = order
	        item.save()
	

#then add to operations list, after migrations.AddField — migrations.RunPython(reorder), and add initial = True, like so:

.. code:: python

	class Migration(migrations.Migration):
	    initial = True
	    dependencies = [
	        ...
	    ]
	    operations = [
	        migrations.AlterModelOptions(
	            ....
	        ),
	        migrations.AddField(
				...
	        ),
	        migrations.RunPython(reorder),
	    ]

then apply the changes to the database using:

.. code:: bash

	shell> ./manage.py migrate myapp

.. note:: If you omit to prepopulate the ordering field with unique values, after adding this field
          to an existing model, then attempting to reorder field manually will fail.


Note on unique indices on the position field
============================================

From a design consideration, one might be tempted to add a unique index on the ordering field. But
in practice this has serious drawbacks:

MySQL has a feature (or bug?) which requires to use the ``ORDER BY`` clause in bulk updates on
unique fields.

SQLite has the same bug which is even worse, because it does neither update all the fields in one
transaction, nor does it allow to use the ``ORDER BY`` clause in bulk updates.

Only PostgreSQL does it "right" in the sense, that it updates all fields in one transaction and
afterwards rebuilds the unique index. Here one can not use the ``ORDER BY`` clause during updates,
which from the point of view for SQL semantics, is senseless anyway.

See https://code.djangoproject.com/ticket/20708 for details.

Therefore I strongly advise against setting ``unique=True`` on the position field, unless you want
unportable code, which only works with Postgres databases.
