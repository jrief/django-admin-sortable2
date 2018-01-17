# -*- coding: utf-8 -*-
import json

from django import VERSION as DJANGO_VERSION
try:
    from django.urls import reverse
except ImportError:  # Django<2.0
    from django.core.urlresolvers import reverse
from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.test import TestCase
from django.test.client import Client, RequestFactory

from testapp.admin import SortableBookAdmin
from testapp.models import SortableBook

User = get_user_model()


class SortableBookTestCase(TestCase):
    if DJANGO_VERSION < (1, 10):
        fixtures = ['data-19.json']
    else:
        fixtures = ['data-110.json']
    admin_password = 'secret'
    ajax_update_url = reverse('admin:testapp_sortablebook_sortable_update')
    bulk_update_url = reverse('admin:testapp_sortablebook_changelist')
    client = Client()
    http_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

    def setUp(self):
        self.loginAdminUser()
        self.site = AdminSite()
        self.factory = RequestFactory()

    def loginAdminUser(self):
        logged_in = self.client.login(username='admin', password=self.admin_password)
        self.assertTrue(logged_in, "Admin user is not logged in")

    def assertUniqueOrderValues(self):
        val = 0
        for obj in SortableBook.objects.order_by('my_order'):
            val += 1
            self.assertEqual(obj.my_order, val, 'Inconsistent order value on SortableBook')

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

    def test_default_order_position(self):
        """
        Ensure that when the field `my_order` is not specified at all,
        the field `_reorder` appears at the beginning of `get_list_display()`.
        """
        request = self.factory.get(self.bulk_update_url)
        old_list = SortableBookAdmin.list_display

        # Ensure that `list_display` does not contain `my_order`
        SortableBookAdmin.list_display = (
            fld for fld in old_list if fld != 'my_order')
        model_admin = SortableBookAdmin(SortableBook, self.site)
        self.assertEqual(
            model_admin.get_list_display(request).index('_reorder'), 0,
            'The order field is not in the correct position.')
        SortableBookAdmin.list_display = old_list

    def test_custom_order_position(self):
        """
        Ensure that if `list_display` has the field `my_order` in a non-zero
        position that the field is replaced by '_reorder' in the same location.
        """
        request = self.factory.get(self.bulk_update_url)
        # old_list = list(SortableBookAdmin.list_display)
        old_list = ['my_order', 'author', 'title']
        new_list = old_list[:]

        # Ensure that `list_display` contains `my_order` in non-zero position.
        try:
            assert old_list.index('my_order') > 0
        except AssertionError:
            # `list_display` contains `my_order` at the start.
            new_list.insert(len(new_list), new_list.pop(0))
            SortableBookAdmin.list_display = new_list
        except ValueError:
            # `list_display` doesn't contain `my_order` at all.
            new_list.append('my_order')
            SortableBookAdmin.list_display = new_list
        my_order_position = new_list.index('my_order')

        # Ensure that `get_list_display()` no longer contains `my_order`, but
        # has `_reorder` in the position that used to contain `my_order`.
        model_admin = SortableBookAdmin(SortableBook, self.site)
        final_list = model_admin.get_list_display(request)
        self.assertFalse('my_order' in final_list,
                         'Field `my_order` is still in `get_list_display()`')
        self.assertEqual(final_list.index('_reorder'), my_order_position,
                         'The order field is not in the correct position')
        SortableBookAdmin.list_display = old_list

    def test_moveUp(self):
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 7)
        in_data = {'startorder': 7, 'endorder': 2}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 3)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 7)

    def test_moveDown(self):
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 7)
        in_data = {'startorder': 7, 'endorder': 12}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 12)
        self.assertEqual(SortableBook.objects.get(pk=8).my_order, 7)

    def test_dontMove(self):
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 7)
        in_data = {'startorder': 7, 'endorder': 6}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=7).my_order, 7)

    def test_reverseMoveUp(self):
        self.assertEqual(SortableBook.objects.get(pk=12).my_order, 12)
        in_data = {'o': '-1', 'startorder': 12, 'endorder': 19}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=12).my_order, 18)
        self.assertEqual(SortableBook.objects.get(pk=13).my_order, 12)
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 16)

    def test_reverseMoveDown(self):
        self.assertEqual(SortableBook.objects.get(pk=12).my_order, 12)
        in_data = {'o': '-1', 'startorder': 12, 'endorder': 7}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=12).my_order, 7)
        self.assertEqual(SortableBook.objects.get(pk=11).my_order, 12)

    def test_reverseDontMove(self):
        self.assertEqual(SortableBook.objects.get(pk=14).my_order, 14)
        in_data = {'o': '-1', 'startorder': 14, 'endorder': 15}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=14).my_order, 14)

    def test_moveFirst(self):
        self.assertEqual(SortableBook.objects.get(pk=2).my_order, 2)
        in_data = {'startorder': 2}
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        self.assertEqual(response.status_code, 200)
        self.assertOrderSequence(in_data, response.content.decode('utf-8'))
        self.assertUniqueOrderValues()
        self.assertEqual(SortableBook.objects.get(pk=2).my_order, 1)

    def test_bulkMovePrevFromFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=14).my_order, 14)
        self.assertEqual(SortableBook.objects.get(pk=15).my_order, 15)
        post_data = {'action': ['move_to_back_page'], 'step': 1, '_selected_action': [14, 15]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=14).my_order, 14)
        self.assertEqual(SortableBook.objects.get(pk=15).my_order, 15)

    def test_bulkMovePreviousPage(self):
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 17)
        self.assertEqual(SortableBook.objects.get(pk=18).my_order, 18)
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 19)
        post_data = {'action': ['move_to_back_page'], 'step': 1, '_selected_action': [17, 18, 19]}
        self.client.post(self.bulk_update_url + '?p=1', post_data)
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=18).my_order, 2)
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 3)

    def test_bulkMoveForwardFromLastPage(self):
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 19)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)
        post_data = {'action': ['move_to_forward_page'], 'step': 1, '_selected_action': [19, 20]}
        self.client.post(self.bulk_update_url + '?p=2', post_data)
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 19)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)

    def test_bulkMoveNextPage(self):
        self.assertEqual(SortableBook.objects.get(pk=11).my_order, 11)
        self.assertEqual(SortableBook.objects.get(pk=10).my_order, 10)
        post_data = {'action': ['move_to_forward_page'], 'step': 1, '_selected_action': [11, 10]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=10).my_order, 13)
        self.assertEqual(SortableBook.objects.get(pk=11).my_order, 14)

    def test_bulkMoveLastPage(self):
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 6)
        post_data = {'action': ['move_to_last_page'], '_selected_action': [1, 6]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 25)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 26)

    def test_bulkMoveFirstPage(self):
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 17)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)
        post_data = {'action': ['move_to_first_page'], '_selected_action': [17, 20]}
        self.client.post(self.bulk_update_url + '?p=2', post_data)
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 2)

    def test_bulkMoveBackTwoPages(self):
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 17)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)
        post_data = {'action': ['move_to_back_page'], 'step': 2, '_selected_action': [17, 20]}
        self.client.post(self.bulk_update_url + '?p=2', post_data)
        self.assertEqual(SortableBook.objects.get(pk=17).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 2)

    def test_bulkMoveForwardTwoPages(self):
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 6)
        post_data = {'action': ['move_to_forward_page'], 'step': 2, '_selected_action': [1, 6]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 25)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 26)

    def test_bulkMoveForwardTwoPagesFromLastPage(self):
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 19)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)
        post_data = {'action': ['move_to_forward_page'], 'step': 2, '_selected_action': [19, 20]}
        self.client.post(self.bulk_update_url + '?p=2', post_data)
        self.assertEqual(SortableBook.objects.get(pk=19).my_order, 19)
        self.assertEqual(SortableBook.objects.get(pk=20).my_order, 20)

    def test_bulkMoveToSpecificPage(self):
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 6)
        post_data = {'action': ['move_to_exact_page'], 'page': 2, '_selected_action': [1, 6]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 13)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 14)

    def test_bulkMoveToSpecificInvalidPage(self):
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 6)
        post_data = {'action': ['move_to_exact_page'], 'page': 10, '_selected_action': [1, 6]}
        self.client.post(self.bulk_update_url, post_data)
        self.assertEqual(SortableBook.objects.get(pk=1).my_order, 1)
        self.assertEqual(SortableBook.objects.get(pk=6).my_order, 6)

    def testFilledBookShelf(self):
        self.assertEqual(SortableBook.objects.count(), 29,
                         'Check fixtures/data.json: Book shelf shall have 29 items')
        self.assertUniqueOrderValues()

    def test_post_save_is_sent_after_reorder(self):
        updated_instances = []
        def listener(sender, instance, **kwargs):
            updated_instances.append(instance.pk)
        in_data = {'startorder': 7, 'endorder': 2}  # from 12345667 to 1273456
        post_save.connect(listener)
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        post_save.disconnect(listener)
        self.assertEqual(len(updated_instances), 5)
        self.assertEqual(updated_instances, [6, 5, 4, 3, 7])

    def test_pre_save_is_sent_before_reorder(self):
        updated_instances = []
        def listener(sender, instance, **kwargs):
            updated_instances.append(instance.pk)
        in_data = {'startorder': 7, 'endorder': 2}  # from 12345667 to 1273456
        pre_save.connect(listener)
        response = self.client.post(self.ajax_update_url, in_data, **self.http_headers)
        pre_save.disconnect(listener)
        self.assertEqual(len(updated_instances), 5)
        self.assertEqual(updated_instances, [7, 6, 5, 4, 3])
