# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from adminsortable import admin
from testapp.models import SortableBook


class SortableBookTestCase(TestCase):
    fixtures = ['data.json']
    admin_password = 'secret'
    update_url = reverse('admin:sortable_update')
    client = Client()
    http_headers = { 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' }

    def setUp(self):
        self.createAdminUser()

    def createAdminUser(self):
        self.user = User.objects.create_user('admin', 'admin@example.com', self.admin_password)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        logged_in = self.client.login(username=self.user.username, password=self.admin_password)
        self.assertTrue(logged_in, 'User is not logged in')

    def assertUniqueOrderValues(self):
        val = 0
        for obj in SortableBook.objects.order_by('order'):
            val += 1
            self.assertEqual(obj.order, val, 'Inconsistent order value on SortableBook')

    def assertOrderSequence(self, in_data, raw_out_data):
        out_data = json.loads(raw_out_data)
        startorder = in_data['startorder']
        endorder = in_data.get('endorder', 0)
        if startorder < endorder:
            self.assertEqual(len(out_data), endorder - startorder)
        elif startorder > endorder + 1:
            self.assertEqual(len(out_data), startorder - endorder)
            startorder, endorder = endorder, startorder
        for k, order in enumerate(range(startorder + 1, endorder)):
            self.assertEqual(order, out_data[k]['order'], 'order value mismatch in out_data')

    def test_moveUp(self):
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)
        in_data = { 'startorder': 7, 'endorder': 2 }
        response = self.client.post(self.update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 3)

    def test_moveDown(self):
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)
        in_data = { 'startorder': 7, 'endorder': 12 }
        response = self.client.post(self.update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 12)

    def test_moveFirst(self):
        self.assertEqual(SortableBook.objects.get(title='The Pragmatic Programmer').order, 2)
        in_data = { 'startorder': 2 }
        response = self.client.post(self.update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='The Pragmatic Programmer').order, 1)

    def test_dontMove(self):
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)
        in_data = { 'startorder': 7, 'endorder': 6 }
        response = self.client.post(self.update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)

    def testFilledBookShelf(self):
        self.assertEqual(SortableBook.objects.count(), 20, 'Check fixtures/data.json: Book shelf shall have 20 items')
        self.assertEqual(SortableBook.objects.all()[0].title, 'The Mythical Man-Month')
        self.assertEqual(SortableBook.objects.reverse()[0].title, 'Django Design Patterns')
        self.assertUniqueOrderValues()
