.. _installation:

============
Installation
============

Install **django-admin-sortable2**. The latest stable release is available on PyPI

.. code-block:: bash

	pip install django-admin-sortable2


Upgrading from version 1
========================

When upgrading from version 1, check for ``StackedInline``- and ``TabularInline``-classes inheriting
from ``SortableInlineAdminMixin``. If they do, check the class inheriting from ``ModelAdmin`` and
using this inline-admin class. Since version 2, this class then also has to inherit from
``SortableAdminBase`` or a class derived of thereof.


Configuration
=============

In the project's ``settings.py`` file add ``'adminsortable2'`` to the list of ``INSTALLED_APPS``:

.. code-block:: python

	INSTALLED_APPS = [
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.admin',
	    'django.contrib.staticfiles',
	    'django.contrib.messages',
	    ...
	    'adminsortable2',
	    ...
	]

The next step is to adopt the models to make them sortable. Please check the page :ref:`usage` for
details.
