import pytest

from django.test import Client
from django.urls import reverse

from testapp.models import Book1

alex_martelli_id = 24


@pytest.mark.django_db
def test_changelist_template_inheritance():
    client = Client()
    response = client.get(reverse('admin:testapp_book7_changelist'))
    assert b"<!-- Import/Export Mixin -->" in response.content


@pytest.mark.django_db
def test_add_book():
    form_data = {
        'title': "Python Cookbook",
        'author': alex_martelli_id,
        '_save': "Save",
    }
    num_books = Book1.objects.count()
    assert Book1.objects.last().my_order == num_books
    client = Client()
    response = client.post(reverse('admin:testapp_book0_add'), form_data)
    assert response.status_code == 302, "Unable to add book"
    assert Book1.objects.count() == num_books + 1
    assert Book1.objects.last().my_order == num_books + 1


@pytest.mark.django_db
def test_add_chapter():
    python_in_a_nutshell = Book1.objects.get(title="Python in a Nutshell")
    assert python_in_a_nutshell.chapter_set.count() == 0
    form_data = {
        'title': "Python in a nutshell",
        'author': alex_martelli_id,
        'chapter_set-TOTAL_FORMS': 2,
        'chapter_set-INITIAL_FORMS': 0,
        'chapter_set-MIN_NUM_FORMS': 0,
        'chapter_set-MAX_NUM_FORMS': 1000,
        'chapter_set-0-title': "Getting Started with Python",
        'chapter_set-0-my_order': "",
        'chapter_set-0-id': "",
        'chapter_set-0-book': python_in_a_nutshell.id,
        'chapter_set-1-title': "Installation",
        'chapter_set-1-my_order': "",
        'chapter_set-1-id': "",
        'chapter_set-1-book': python_in_a_nutshell.id,
        '_save': "Save",
    }
    client = Client()
    response = client.post(reverse('admin:testapp_book3_change', args=(python_in_a_nutshell.id,)), form_data)
    assert response.status_code == 302, "Unable to add chapter"
    assert python_in_a_nutshell.chapter_set.count() == 2
    assert python_in_a_nutshell.chapter_set.first().my_order == 1
    assert python_in_a_nutshell.chapter_set.last().my_order == 2
