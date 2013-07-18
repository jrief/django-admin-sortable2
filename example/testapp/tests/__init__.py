# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client, RequestFactory
from adminsortable import admin
from testapp.models import SortableBook


class SortableBookTestCase(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def testBookShelf(self):
        self.assertEqual(SortableBook.objects.count(), 20, 'Check fixtures/data.json: Book shelf shall have 20 items')
        self.assertEqual(SortableBook.objects.all()[0], 'The Mythical Man-Month')
        self.assertEqual(SortableBook.objects.all()[19], 'Django Design Patterns')
