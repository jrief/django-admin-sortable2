.. _contributing:

===========================
Contributing to the Project
===========================

* Please ask question on the `discussion board`_.
* Ideas for new features also shall be discussed on that board.
* The `issue tracker`_ shall *exclusively* be used to report bugs.
* Except for very small fixes, do not open a pull request without an issue.

.. _discussion board: https://github.com/jrief/django-admin-sortable2/discussions/
.. _issue tracker: https://github.com/jrief/django-admin-sortable2/issues


Writing Code
============

Adopt your IDE to respect the projects's `.editorconfig`_ file.

When installing from GitHub, you *must* build the client using the esbuild_ TypeScript compiler:

.. code-block:: shell

	cd django-admin-sortable2
	npm install --also=dev
	npm run build

This then builds and bundles the JavaScript file
`adminsortable2/static/adminsortable2/js/adminsortable2.js` which then is included by the mixin
classes.

.. _.editorconfig: https://editorconfig.org/
.. _esbuild: https://esbuild.github.io/


Running Tests
=============

In version 2, unit tests have been replaced by end-to-end tests using Playwright-Python_
using pytest-django_ as test runner. Run these tests using:

.. code-block:: shell
	cd django-admin-sortable2
	python -m pip install -r testapp/requirements.txt
	python -m playwright install
	python -m playwright install-deps
	python -m pytest testapp

.. _Playwright-Python: https://playwright.dev/python/
.. _pytest-django: https://pytest-django.readthedocs.io/en/latest/


Quoting
=======

Please follow this rule when quoting string:

* A string intended to be read by humans shall be quoted using double quotes: `"…"`.
* An internal string, such as dictionary keys, etc. not intended to be read by humans
  shall be quoted using single quotes: `'…'`.
