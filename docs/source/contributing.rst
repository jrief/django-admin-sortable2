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
	npm install --also=dev
	npm run build

This then builds and bundles the JavaScript file
``adminsortable2/static/adminsortable2/js/adminsortable2.js`` which later on is included by the
mixin classes.

.. _.editorconfig: https://editorconfig.org/
.. _esbuild: https://esbuild.github.io/


Run the Demo App
================

**django-admin-sotable2** is shipped with a demo app, which shall be used as a reference when
reporting bugs, proposing new features or to just get a quick first impression of this library.

Follow these steps to run this demo app.

.. code:: bash

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2
	npm install --also=dev
	npm run build
	python -m pip install -r testapp/requirements.txt
	cd testapp
	./manage.py migrate
	./manage.py loaddata fixtures/data.json
	./manage.py runserver

Point a browser onto http://localhost:8000/admin/, and go to **Testapp > Books**. There you
can test the full set of features available in this library.

In section **TESTAPP** there are four models named "Book". They only differ in the way their default
sorting is organized: Somtimes by the model, somtimes for the admin interface and in both sorting
directions. So don't be confused about seeing different editors for exactly the same model.


Running Tests
=============

In version 2.0, many unit tests have been replaced by end-to-end tests using Playwright-Python_. In
addition, the Django test runner has been replaced by pytest-django_.

Follow these steps to run all unit- and end-to-end tests.

.. code-block:: shell

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2
	npm install --also=dev
	npm run build
	python -m pip install -r testapp/requirements.txt
	python -m playwright install
	python -m playwright install-deps
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
  humans), shall be quoted using single quotes: `'…'`.


Lists versus Tuples
===================

Unfortunately in Django, `we developers far too often`_ intermixed lists and tuples without being
aware of their intention. Therefor please follow this rule:

Always use lists, if there is a theoretical possibility that someday, someone might add an item.
Therefore ``list_display``, ``list_display_links``, ``fields``, etc. shall always be lists.

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
