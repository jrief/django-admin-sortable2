# django-admin-sortable2

A replacement for django-admin-sortable using an unintrusive approach.

[![Build Status](https://github.com/jrief/django-admin-sortable2/actions/workflows/django.yml/badge.svg)](https://github.com/jrief/django-admin-sortable2/actions/workflows/django.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-admin-sortable2.svg)](https://pypi.python.org/pypi/django-admin-sortable2)
[![Python versions](https://img.shields.io/pypi/pyversions/django-admin-sortable2.svg)](https://pypi.python.org/pypi/django-admin-sortable2)
[![Django versions](https://img.shields.io/pypi/djversions/django-admin-sortable2)](https://pypi.python.org/pypi/django-admin-sortable2)
[![Downloads](https://img.shields.io/pypi/dm/django-admin-sortable2.svg)](https://img.shields.io/pypi/dm/django-admin-sortable2.svg)
[![Software license](https://img.shields.io/pypi/l/django-admin-sortable2.svg)](https://github.com/jrief/django-admin-sortable2/blob/master/LICENSE)

This plugin is a generic drag-and-drop ordering module for sorting objects in the List, the Stacked-
and the Tabular-Inlines Views in the Django Admin interface.

![Demo](https://raw.githubusercontent.com/jrief/django-admin-sortable2/master/demo.gif)

This module offers simple mixin classes which enrich the functionality of any existing class derived
from `admin.ModelAdmin`, `admin.StackedInline` or `admin.TabularInline`.

Thus it makes it very easy to integrate with existing models and their model admin interfaces.
Existing models can inherit from `models.Model` or any other class derived thereof. No special
base class is required.


## Project's home

https://github.com/jrief/django-admin-sortable2

Detailled documentation on [ReadTheDocs](http://django-admin-sortable2.readthedocs.org/en/latest/).

To ask questions or reporting bugs, please use the [issue tracker](https://github.com/jrief/django-admin-sortable2/issues).


## Why should You use it?

All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of `models.Model`. This abstract base class then
contains a hard coded position field, additional methods, and meta directives.

This inhibits to create sortable abstract models. **django-admin-sortable2** does not have these
restrictions.


## License

MIT licensed.

Copyright &copy; 2013-2021 Jacob Rief and contributors.

[![Twitter Follow](https://img.shields.io/twitter/follow/jacobrief.svg?style=social&label=Jacob+Rief)](https://twitter.com/jacobrief)
