import pytest

from django.test import Client
from django.urls import reverse

from testapp.models import SortableBook3


alex_martelli_id = 24


@pytest.mark.django_db
def test_add_book():
    form_data = {
        'title': "Python Cookbook",
        'author': alex_martelli_id,
        '_save': "Save",
    }
    num_books = SortableBook3.objects.count()
    assert SortableBook3.objects.last().my_order == num_books
    client = Client()
    response = client.post(reverse('admin:testapp_sortablebook_add'), form_data)
    assert response.status_code == 302, "Unable to add book"
    assert SortableBook3.objects.count() == num_books + 1
    assert SortableBook3.objects.last().my_order == num_books + 1

