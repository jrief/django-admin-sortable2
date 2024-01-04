.. _contributing:

===========================
Contributing to the Project
===========================

* Please ask question on the `discussion board`_.
* Ideas for new features also shall be discussed on that board as well.
* The `issue tracker`_ shall *exclusively* be used to report bugs.
* Except for very small fixes (typos etc.), do not open a pull request without an issue.

.. _discussion board: https://github.com/jrief/django-admin-sortable2/discussions/
.. _issue tracker: https://github.com/jrief/django-admin-sortable2/issues


Writing Code
============

Before hacking into the code, adopt your IDE to respect the projects's `.editorconfig`_ file.

When installing from GitHub, you *must* build the JavaScript client using the esbuild_ TypeScript
compiler:

.. code-block:: shell

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2
	npm install
	npm run build

	# and optionally for a minimized version
	npm run minify

This then builds and bundles the JavaScript file
``adminsortable2/static/adminsortable2/js/adminsortable2.js`` which later on is imported by the
sortable-admin mixin classes. The minimized version can be imported as
``adminsortable2/static/adminsortable2/js/adminsortable2.min.js``

.. _.editorconfig: https://editorconfig.org/
.. _esbuild: https://esbuild.github.io/


Run the Demo App
================

**django-admin-sortable2** is shipped with a demo app, which shall be used as a reference when
reporting bugs, proposing new features or to just get a quick first impression of this library.

Follow these steps to run this demo app. Note that in addition to Python, you also need a recent
version of NodeJS.

.. code:: bash

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2
	npm install
	npm run build
	npm run minify
	python -m pip install Django
	python -m pip install -r testapp/requirements.txt

	# we use the default template files and patch them, rather than using our own modified one
	django_version=$(python -c 'from django import VERSION; print("{0}.{1}".format(*VERSION))')
	mkdir adminsortable2/templates/adminsortable2/edit_inline
	curl --no-progress-meter --output adminsortable2/templates/adminsortable2/edit_inline/stacked-django-$django_version.html https://raw.githubusercontent.com/django/django/stable/$django_version.x/django/contrib/admin/templates/admin/edit_inline/stacked.html
	curl --no-progress-meter --output adminsortable2/templates/adminsortable2/edit_inline/tabular-django-$django_version.html https://raw.githubusercontent.com/django/django/stable/$django_version.x/django/contrib/admin/templates/admin/edit_inline/tabular.html
	patch -p0 adminsortable2/templates/adminsortable2/edit_inline/stacked-django-$django_version.html patches/stacked-django-4.0.patch
	patch -p0 adminsortable2/templates/adminsortable2/edit_inline/tabular-django-$django_version.html patches/tabular-django-4.0.patch

	cd testapp
	./manage.py migrate
	./manage.py loaddata fixtures/data.json
	./manage.py runserver

Point a browser onto http://localhost:8000/admin/, and go to **Testapp > Books**. There you
can test the full set of features available in this Django app.

In section **TESTAPP** there are eight entires named "Book". They all manage the same database model
(ie. ``Book``) and only differ in the way their sorting is organized: Somtimes by the Django model,
somtimes by the Django admin class and in both sorting directions.


Reporting Bugs
==============

For me it often is very difficult to comprehend why this library does not work with *your* project.
Therefore wheneever you want to report a bug, **report it in a way so that I can reproduce it**.

**Checkout the code, build the client and run the demo** as decribed in the previous section.
Every feature offered by **django-admin-sortable2** is implemented in the demo named ``testapp``.
If you can reproduce the bug there, report it. Otherwise check why your application behaves
differently.


Running Tests
=============

In version 2.0, many unit tests have been replaced by end-to-end tests using Playwright-Python_. In
addition, the Django test runner has been replaced by pytest-django_.

Follow these steps to run all unit- and end-to-end tests.

.. code-block:: shell

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2
	npm install
	npm run build
	python -m pip install Django
	python -m pip install -r testapp/requirements.txt
	python -m playwright install
	python -m playwright install-deps

	# we use the default template files and patch them, rather than using our own modified one
	django_version=$(python -c 'from django import VERSION; print("{0}.{1}".format(*VERSION))')
	mkdir adminsortable2/templates/adminsortable2/edit_inline
	curl --no-progress-meter --output adminsortable2/templates/adminsortable2/edit_inline/stacked-django-$django_version.html https://raw.githubusercontent.com/django/django/stable/$django_version.x/django/contrib/admin/templates/admin/edit_inline/stacked.html
	curl --no-progress-meter --output adminsortable2/templates/adminsortable2/edit_inline/tabular-django-$django_version.html https://raw.githubusercontent.com/django/django/stable/$django_version.x/django/contrib/admin/templates/admin/edit_inline/tabular.html
	patch -p0 adminsortable2/templates/adminsortable2/edit_inline/stacked-django-$django_version.html patches/stacked-django-4.0.patch
	patch -p0 adminsortable2/templates/adminsortable2/edit_inline/tabular-django-$django_version.html patches/tabular-django-4.0.patch

	python -m pytest testapp

.. _Playwright-Python: https://playwright.dev/python/
.. _pytest-django: https://pytest-django.readthedocs.io/en/latest/


Adding new Features
===================

If you want to add a new feature to **django-admin-sortable2**, please integrate a demo into the
testing app (ie. ``testapp``). Doing so has two benefits:

I can understand way better what it does and how that new feature works. This increases the chances
that such a feature is merged.

You can use that extra code to adopt the test suite.

*Remember*: For UI-centric applications such as this one, where the client- and server-side are
strongly entangled with each other, I prefer end-to-end tests way more rather than unit tests.
Reason is, that otherwise I would have to mock the interfaces, which itself is error-prone and
additional work.

*Don't hide yourself*: I will not accept large pull requests from anonymous users, so please publish
an email address in your GitHub's profile. Reason is that when refactoring the code, I must be
able to contact the initial author of a feature not added by myself.


Quoting
=======

Please follow these rules when quoting strings:

* A string intended to be read by humans shall be quoted using double quotes: `"…"`.
* An internal string, such as dictionary keys, etc. (and thus usually not intended to be read by
  humans), shall be quoted using single quotes: `'…'`. This makes it easier to determine if we have
  to extra check for wording.

There is a good reason to follow this rule: Strings intended for humans, sometimes contain
apostrophes, for instance `"This is John's profile"`. By using double quotes, those apostrophes must
not be escaped. On the other side whenever we write HTML, we have to use double quotes for
parameters, for instance `'<a href="https://example.org">Click here!</a>'`. By using single quotes,
those double quotes must not be escaped.


Lists versus Tuples
===================

Unfortunately in Django, `we developers far too often`_ intermixed lists and tuples without being
aware of their intention. Therefore please follow this rule:

Always use lists, if there is a theoretical possibility that someday, someone might add another
item. Therefore ``list_display``, ``list_display_links``, ``fields``, etc. must always be lists.

Always use tuples, if the number of items is restricted by nature, and there isn't even a
theoretical possibility of being extended.

Example:

.. code-block:: python

	color = ChoiceField(
	    label="Color",
	    choices=[('ff0000', "Red"), ('00ff00', "Green"), ('0000ff', "Blue")],
	)

A ``ChoiceField`` must provide a list of choices. Attribute ``choices`` must be a list because
it is eligible for extension. Its inner items however must be tuples, because they can exlusively
containin the choice value and a human readable label. Here we also intermix single with double
quotes to distinguish strings intended to be read by the machine versus a human.

.. _we developers far too often: https://groups.google.com/g/django-developers/c/h4FSYWzMJhs
