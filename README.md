django-admin-sortable2
======================

A replacement for django-admin-sortable using an unintrusive approach.

This plugin is a generic drag-and-drop ordering module for sorting objects in the List, the Stacked-
and the Tabular-Inlines Views in the Django Admin interface.

This module offers simple mixin classes which enrich the functionality of any existing class derived
from ``admin.ModelAdmin``, ``admin.StackedInline`` or ``admin.TabularInline``.

Thus it makes it very easy to integrate with existing models and their model admin interfaces.
Existing models can inherit from ``models.Model`` or any other class derived thereof. No special
base class is required.


News in Version 0.6.4
---------------------

* Drop support for Django-1.7 and lower.
* Feature request #107: Overidable SortableAdminMixin.get_max_order(request, obj)
# Fixed #100: actions = none breaks functionality
* Fixed #98: js error in admin
* Fixed #55: TabularInline template THEAD colspan=2 broken
* Fixed #82: SortableInlineAdminMixin screws up TabularInline colums
* Fixed #104: Key 'order' not found

Many thanks to @rubengrill for fixing them!


Project's home
--------------
https://github.com/jrief/django-admin-sortable2.

Detailled documentation on [ReadTheDocs](http://django-admin-sortable2.readthedocs.org/en/latest/).

To ask questions or reporting bugs, please use the [issue tracker](https://github.com/jrief/django-admin-sortable2/issues).


Build status
------------

[![Build Status](https://travis-ci.org/jrief/django-admin-sortable2.png?branch=master)](https://travis-ci.org/jrief/django-admin-sortable2)


Why should You use it?
----------------------
All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of ``models.Model``. This abstract base class then
contains a hard coded position field, additional methods, and meta directives.

This inhibits to create sortable abstract models. **django-admin-sortable2** does not have these
restrictions.


License
-------

Copyright &copy; 2016 Jacob Rief.

MIT licensed.
