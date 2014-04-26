.. _demos:

================
Run Example Code
================

To get a quick first impression of this plugin, clone this repositoty
from GitHub and run an example webserver:

.. code:: bash

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2/example/
	./manage.py syncdb
	# add an admin user
	./manage.py loaddata testapp/fixtures/data.json
	./manage.py runserver

Point a browser onto http://localhost:8000/admin/, log in and go to *Sortable books*. There you can
test the behavior of this Django app.
