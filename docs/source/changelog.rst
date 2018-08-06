.. _changelog:

===============
Release history
===============

0.6.21
------
* Added jQuery compatibility layer for Django-2.1.

0.6.20
------
* Dysfunctional.

0.6.19
------
* Fix #183: Use ``mark_safe`` for reorder ``div``.

0.6.18
------
* Fixes meth:`adminsortable2.admin.SortableInlineAdminMixin.get_fields`: Always return
  a list instead of sometimes a tuple.

0.6.17
------
* Fixes #171: Adhere to Content Security Policy best practices by removing inline scripts.
* Adopted to Django-2.0 keeping downwards compatibility until Django-1.9.
* Better explanation what to do in case of sorting inconsistency.

0.6.16
------
* Fixes #137: Allow standard collapsible tabular inline.

0.6.15
------
* Fixes #164: TypeError when ``display_list`` in admin contains a callable.
* Fixes #160: Updated ordering values not getting saved in Tabluar/StackedInlineAdmin.

0.6.14
------
* Fixes #162: In model admin, setting ``actions`` to ``None`` or ``[]`` breaks the
  sortable functionality.

0.6.13
------
* Fixes #159: Make stacked inline's header more clear that it is sortable.

0.6.12
------
* Fixes #155: Sortable column not the first field by default.

0.6.11
------
* Fixes #147: Use current admin site name instead of 'admin'.
* Fixes #122: Columns expand continuously with each sort.

0.6.9 and 0.6.10
----------------
* Fixes Issue #139: better call of post_save signal.

0.6.8
-----
* Fixes Issue #135: better call of pre_save signal.
* On ``./manage.py reorder ...``, name the model using ``app_label.model_name`` rather than
  requiring the fully qualified path.
* In :class:`adminsortable2.admin.SortableAdminMixin` renamed method ``update`` to ``update_order``,
  to prevent potential naming conflicts.

0.6.7
-----
* Added class ``PolymorphicSortableAdminMixin`` so that method ``get_max_order`` references
  the ordering field from the base model.


0.6.6
-----
* Fixed: Drag'n Drop reordering now send [pre|post]_save signals for all updated instances.

0.6.5
-----
* Fixed: Reorder management command now accepts args.


0.6.4
-----
* Drop support for Django-1.5.
* change_list_template now is extendible.
* Fixed concatenation if ``exclude`` is tuple.
* Support reverse sorting in CustomInlineFormSet.

0.6.3
-----
* setup.py ready for Python 3.

0.6.2
-----
* Fixed regression from 0.6.0: Multiple sortable inlines are now possible again.

0.6.1
-----
* Removed global variables from Javascript namespace.

0.6.0
-----
* Compatible with Django 1.9.
* In the list view, it now is possible to move items to any arbitrary page.

0.5.0
-----
* Changed the namespace from adminsortable to adminsortable2 to allow both this
  project and django-admin-sortable to co-exist in the same project. This is
  helpful for projects to transition from one to the other library. It also allows
  existing projects's migrations which previously relied on django-admin-sortable
  to continue to work.

0.3.2
-----
* Fixed #42: Sorting does not work when ordering is descending.

0.3.2
-----
* Using property method ``media()`` instead of hard coded ``Media`` class.
* Using the ``verbose_name`` from the column used to keep the order of fields instead of a hard
  coded "Sort".
* When updating order in change_list_view, use the CSRF protection token.

0.3.1
-----
* Fixed issue #25: admin.TabularInline problem in django 1.5.x
* Fixed problem when adding new Inline Form Fields.
* PEP8 cleanup.

0.3.0
-----
* Support for Python-3.3.
* Fixed: Add list-sortable.js on changelist only. Issue #31.

0.2.9
-----
* Fixed: StackedInlines do not add an empty field after saving the model.
* Added management command to preset initial ordering.

0.2.8
-----
* Refactored documentation for Read-The-Docs

0.2.7
-----
* Fixed: MethodType takes only two attributes

0.2.6
-----
* Fixed: Unsortable inline models become draggable when there is a sortable inline model

0.2.5
-----
* Bulk actions are added only when they make sense.
* Fixed bug when clicking on table header for ordering field.

0.2.4
-----
* Fix CustomInlineFormSet to allow customization. Thanks **yakky**.

0.2.2
-----
* Distinction between different versions of jQuery in case django-cms is installed side by side.

0.2.0
-----
* Added sortable stacked and tabular inlines.

0.1.2
-----
* Fixed: All field names other than "order" are now allowed.

0.1.1
-----
* Fixed compatibility issue when used together with django-cms.

0.1.0
-----
* First version published on PyPI.

0.0.1
-----
First working release.
