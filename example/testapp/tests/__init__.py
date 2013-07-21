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
        if in_data.get('o', '').split('.')[0] != '-1':
            order_up, order_down = 0, 1
        else:
            order_up, order_down = 1, 0
        if startorder < endorder - order_up:
            self.assertEqual(len(out_data), endorder - startorder + order_down)
        elif startorder > endorder + order_down:
            self.assertEqual(len(out_data), startorder - endorder + order_up)
        else:
            self.assertEqual(len(out_data), 0)

    def test_moveUp(self):
        self.assertEqual(SortableBook.objects.get(pk=7).order, 7)
        in_data = { 'startorder': 7, 'endorder': 2 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).order, 3)
        self.assertEqual(SortableBook.objects.get(pk=6).order, 7)

    def test_moveDown(self):
        self.assertEqual(SortableBook.objects.get(pk=7).order, 7)
        in_data = { 'startorder': 7, 'endorder': 12 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).order, 12)
        self.assertEqual(SortableBook.objects.get(pk=8).order, 7)

    def test_dontMove(self):
        self.assertEqual(SortableBook.objects.get(pk=7).order, 7)
        in_data = { 'startorder': 7, 'endorder': 6 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).order, 7)

    def test_reverseMoveUp(self):
        self.assertEqual(SortableBook.objects.get(pk=12).order, 12)
        in_data = { 'o': '-1', 'startorder': 12, 'endorder': 17 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=12).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=13).order, 12)

    def test_reverseMoveDown(self):
        self.assertEqual(SortableBook.objects.get(pk=12).order, 12)
        in_data = { 'o': '-1', 'startorder': 12, 'endorder': 7 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=12).order, 7)
        self.assertEqual(SortableBook.objects.get(pk=11).order, 12)

    def test_reverseDontMove(self):
        self.assertEqual(SortableBook.objects.get(pk=14).order, 14)
        in_data = { 'o': '-1', 'startorder': 14, 'endorder': 15 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=14).order, 14)

    def test_moveFirst(self):
        self.assertEqual(SortableBook.objects.get(pk=2).order, 2)
        in_data = { 'startorder': 2 }
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content)
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=2).order, 1)

    def test_bulkMovePrevFromFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=14).order, 14)
        self.assertEqual(SortableBook.objects.get(pk=15).order, 15)
        post_data = { 'action': ['move_to_prev_page'], '_selected_action': [14, 15] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=14).order, 14)
        self.assertEqual(SortableBook.objects.get(pk=15).order, 15)

    def test_bulkMovePreviousPage(self):
        self.assertEqual(SortableBook.objects.get(pk=17).order, 17)
        self.assertEqual(SortableBook.objects.get(pk=18).order, 18)
        self.assertEqual(SortableBook.objects.get(pk=19).order, 19)
        post_data = { 'p': 1, 'action': ['move_to_prev_page'], '_selected_action': [17, 18, 19] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=17).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=18).order, 2)
        self.assertEqual(SortableBook.objects.get(pk=19).order, 3)

    def test_bulkMoveNextPage(self):
        self.assertEqual(SortableBook.objects.get(pk=11).order, 11)
        self.assertEqual(SortableBook.objects.get(pk=12).order, 12)
        post_data = { 'action': ['move_to_next_page'], '_selected_action': [11, 12] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=11).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=12).order, 17)

    def test_bulkMoveLastPage(self):
        self.assertEqual(SortableBook.objects.get(pk=1).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=9).order, 9)
        post_data = { 'action': ['move_to_last_page'], '_selected_action': [1, 9] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=9).order, 17)

    def test_bulkMoveFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=16).order, 16)
        self.assertEqual(SortableBook.objects.get(pk=20).order, 20)
        post_data = { 'p': 1, 'action': ['move_to_first_page'], '_selected_action': [16, 20] }
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=16).order, 1)
        self.assertEqual(SortableBook.objects.get(pk=20).order, 2)

    def testFilledBookShelf(self):
        self.assertEqual(SortableBook.objects.count(), 20, 'Check fixtures/data.json: Book shelf shall have 20 items')
        self.assertUniqueOrderValues()
