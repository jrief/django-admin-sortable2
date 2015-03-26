.. _installation:

============
Installation
============

Install **django-admin-sortable2**. The latest stable release can be found on PyPI

.. code-block:: bash

	pip install django-admin-sortable2

or the newest development version from GitHub

.. code-block:: bash

	pip install -e git+https://github.com/jrief/django-admin-sortable2#egg=django-admin-sortable2

Configuration
=============

Add ``'adminsortable2'`` to the list of ``INSTALLED_APPS`` in your project's ``settings.py`` file

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'adminsortable2',
	    ...
	)
