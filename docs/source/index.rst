.. adminsortable2 documentation master file

======================
django-admin-sortable2
======================
This Django module is as a replacement for `django-admin-sortable`_ using an unintrusive approach.

It is a generic drag-and-drop ordering module for sorting objects in the list view of the Django
admin interface. This plugin offers simple mixin classes which enrich the functionality of *any*
existing class derived from ``admin.ModelAdmin``, ``admin.StackedInline`` or
``admin.TabularInline``. It thus makes it very easy to integrate with existing models and their
model admin interfaces.

.. _django-admin-sortable: https://github.com/iambrandontaylor/django-admin-sortable

Project home: https://github.com/jrief/django-admin-sortable2

Please ask questions and report bugs on: https://github.com/jrief/django-admin-sortable2/issues

Why another adminsortable plugin?
=================================
All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of ``models.Model``. This abstract base class then
contains a hard coded position field, additional methods, and meta directives. The problem with such
an approach is twofold:

First, an *is-a* relationship is abused to enrich the functionality of a class. This is bad OOP
practice. A base class shall only be used to reflect a real *is-a* relation which specializes this
class. For instance: A mammal *is an* animal, a primate *is a* mammal, homo sapiens *is a*
primate, etc. Here the inheritance model is appropriate, but it would be wrong to derive from
homo sapiens to reflect a human which is able to hunt using bows and arrows.

Therefore, a sortable model *is not an* unsortable model. Making a Django Model sortable enriches its
functionality. In OOP design this does not qualify for an *is-a* relationship.

Fortunately, Python makes it very easy to distinguish between real *is-a* relationships and
interfaces enriching their functionality. The latter are handled by so named mixin classes. They
offer additional methods for a class without deriving from the base class.

Also consider the case when someone wants to augment some other functionality of a model class. If
he also derives from ``models.Model``, he would create another abstract intermediate class.
Someone who wants to use *both* functional augmentations, now is in trouble. He has to choose
between one of the two, as he cannot derive from both of them, because then its model class would
inherit the base class ``models.Model`` twice. This kind of diamond-shaped inheritance is to be avoided
under all circumstances.

By using a mixin class rather than deriving from a special abstract base class, these problems can
be avoided!

Contents:
=========
.. toctree::

  installation
  usage
  demos
  changelog

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
=======
Copyright © 2017 Jacob Rief.
Licensed under the MIT license.

Some Related projects
=====================
* https://github.com/iambrandontaylor/django-admin-sortable
* https://github.com/mtigas/django-orderable
* http://djangosnippets.org/snippets/2057/
* http://djangosnippets.org/snippets/2306/
* http://catherinetenajeros.blogspot.co.at/2013/03/sort-using-drag-and-drop.html
