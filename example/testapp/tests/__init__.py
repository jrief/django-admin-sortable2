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
    ajax_update_url = reverse('admin:sortable_update')
    bulk_update_url = reverse('admin:testapp_sortablebook_changelist')
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
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 3)

    def test_moveDown(self):
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)
        in_data = { 'startorder': 7, 'endorder': 12 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 12)

    def test_moveFirst(self):
        self.assertEqual(SortableBook.objects.get(title='The Pragmatic Programmer').order, 2)
        in_data = { 'startorder': 2 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='The Pragmatic Programmer').order, 1)

    def test_dontMove(self):
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)
        in_data = { 'startorder': 7, 'endorder': 6 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(title='Code Complete').order, 7)

    def test_bulkMovePrevFromFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=15).order, 14)
        self.assertEqual(SortableBook.objects.get(pk=17).order, 15)
        post_data = { 'action': ['move_to_prev_page'], '_selected_action': [15, 17] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=15).order, 14)
        self.assertEqual(SortableBook.objects.get(pk=17).order, 15)

    def test_bulkMovePreviousPage(self):
        self.assertEqual(SortableBook.objects.get(pk=19).order, 17)
        self.assertEqual(SortableBook.objects.get(pk=21).order, 18)
        self.assertEqual(SortableBook.objects.get(pk=20).order, 19)
        post_data = { 'p': 1, 'action': ['move_to_prev_page'], '_selected_action': [19, 21, 20] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=19).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=21).order, 2)
        self.assertEqual(SortableBook.objects.get(pk=20).order, 3)

    def test_bulkMoveNextPage(self):
        self.assertEqual(SortableBook.objects.get(pk=12).order, 11)
        self.assertEqual(SortableBook.objects.get(pk=13).order, 12)
        post_data = { 'action': ['move_to_next_page'], '_selected_action': [12, 13] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=12).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=13).order, 17)

    def test_bulkMoveLastPage(self):
        self.assertEqual(SortableBook.objects.get(pk=1).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=10).order, 9)
        post_data = { 'action': ['move_to_last_page'], '_selected_action': [1, 10] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=10).order, 17)

    def test_bulkMoveFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=18).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=16).order, 20)
        post_data = { 'p': 1, 'action': ['move_to_first_page'], '_selected_action': [18, 16] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=18).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=16).order, 2)

    def testFilledBookShelf(self):
        self.assertEqual(SortableBook.objects.count(), 20, 'Check fixtures/data.json: Book shelf shall have 20 items')
        self.assertEqual(SortableBook.objects.all()[0].title, 'The Mythical Man-Month')
        self.assertEqual(SortableBook.objects.reverse()[0].title, 'Django Design Patterns')
        self.assertUniqueOrderValues()
