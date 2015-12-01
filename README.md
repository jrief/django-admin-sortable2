django-admin-sortable2
======================

A replacement for django-admin-sortable using an unintrusive approach.

This plugin is a generic drag-and-drop ordering module for sorting objects in the List, the Stacked-
and the Tabular-Inlines Views in the Django Admin interface.

This module offers simple mixin classes which enrich the functionality of any existing class derived
from ``admin.ModelAdmin``, ``admin.StackedInline`` or ``admin.TabluarInline``.

Thus it makes it very easy to integrate with existing models and their model admin interfaces.
Existing models can inherit from ``models.Model`` or any other class derived thereof. No special
base class is required.


News in Version 0.6.0
---------------------

Many Thanks to Michał Przybyś for adding these two features:

* Compatible with Django 1.9.
* In the list view, it now is possible to move items to any arbitrary page.


Project's home
--------------
https://github.com/jrief/django-admin-sortable2.

Detailled documentation on [ReadTheDocs](http://django-admin-sortable2.readthedocs.org/en/latest/).

To ask questions or reporting bugs, please use the [issue tracker](https://github.com/jrief/django-admin-sortable2/issues).


Build status
------------

[![Build Status](https://travis-ci.org/jrief/django-admin-sortable2.png?branch=master)](https://travis-ci.org/jrief/django-admin-sortable2)
[![Downloads](http://img.shields.io/pypi/dm/django-admin-sortable2.svg?style=flat-square)](https://pypi.python.org/pypi/django-admin-sortable2/)


Why should You use it?
----------------------
All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of ``models.Model``. This abstract base class then
contains a hard coded position field, additional methods, and meta directives.

This inhibits to create sortable abstract models. **django-admin-sortable2** does not have these
restrictions.


License
-------

Copyright &copy; 2015 Jacob Rief.

MIT licensed.
