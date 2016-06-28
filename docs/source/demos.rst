.. _demos:

================
Run Example Code
================

To get a quick first impression of this plugin, clone this repositoty
from GitHub and run an example webserver:

.. code:: bash

	git clone https://github.com/jrief/django-admin-sortable2.git
	cd django-admin-sortable2/example/
	./manage.py migrate
	./manage.py createsuperuser --username admin --email admin@example.org
	./manage.py loaddata testapp/fixtures/data.json
	./manage.py runserver

Point a browser onto http://localhost:8000/admin/, sign in as ``admin`` and go to
**Testapp > Sortable books**. There you can test the behavior of **django-admin-sortable2**.
