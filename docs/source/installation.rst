.. _installation:

============
Installation
============

Install **django-admin-sortable2**. The latest stable release can be found on PyPI

.. code-block:: bash

	pip install django-admin-sortable2


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

The next step is to adopt the models in order to make them sortable. Please check the page
:ref:`usage` for details.
