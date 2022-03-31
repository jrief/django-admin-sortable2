.. adminsortable2 documentation master file

======================
django-admin-sortable2
======================

is a generic drag-and-drop ordering package to sort objects in the list- and detail inline-views
of the Django admin interface. This package offers simple mixin classes which enriches the
functionality of *any* existing class derived from ``admin.ModelAdmin``, ``admin.StackedInline``
or ``admin.TabularInline``. It thus makes it very easy to integrate with existing models and their
model admin interfaces.

Project home: https://github.com/jrief/django-admin-sortable2

.. image:: _static/django-admin-sortable2.gif
  :width: 800
  :alt: django-admin-sortable2 demo


Why another adminsortable plugin?
=================================

All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of ``models.Model``. This abstract base class then
contains a hard coded position field, additional methods, and meta directives. The problem with such
an approach is twofold:

First, an *is-a* relationship is abused to enrich the functionality of a class. This is bad OOP
practice. A base class shall only be used to reflect real *is-a* relations when specializing a
derived class. For instance: A mammal *is an* animal, a primate *is a* mammal, homo sapiens *is a*
primate, etc. Here the inheritance model is appropriate, but it would be wrong to derive from
homo sapiens to reflect a human which is able to hunt using bows and arrows.

Therefore, a sortable model *is not an* unsortable model. Making a Django Model sortable enriches
its functionality. In OOP design this does not qualify for an *is-a* relationship.

Fortunately, Python makes it very easy to distinguish between real *is-a* relationships and
interfaces enriching their functionality. The latter are handled by mixin classes. They
offer additional methods for classes without inheriting from the given base class.

Also consider the case when we want to augment some other functionality of a model class. If
we also inherit from ``models.Model``, we would create another abstract intermediate class.
If we want to use *both* functional augmentations, we now are in trouble. We have to choose
between one of the two, as we cannot inherit from both of them, because then our Django model
would inherit from the base class ``models.Model`` twice. This kind of diamond-shaped inheritance
shall be avoided.

By using a mixin to enrich an existing class with sorting functionality rather than inheriting
from a special abstract base class, we can avoid these problems.


Contents:
=========
.. toctree::

  installation
  usage
  contributing


License
=======

Copyright Jacob Rief and contributors.

Licensed under the terms of the MIT license.


Some Related projects
=====================

* https://github.com/jazzband/django-admin-sortable
* https://github.com/mtigas/django-orderable
* https://djangosnippets.org/snippets/2057/
* https://djangosnippets.org/snippets/2306/
