import json
import re

import pytest

from django.test import Client, override_settings
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


@pytest.mark.django_db
@override_settings(CSRF_USE_SESSIONS=True, CSRF_HEADER_NAME='HTTP_X_AUTH_CSRFTOKEN')
def test_sortable_respects_custom_csrf_header_name():
    client = Client(enforce_csrf_checks=True)
    changelist_response = client.get(reverse('admin:testapp_book1_changelist'))
    assert changelist_response.status_code == 200

    content = changelist_response.content.decode('utf-8')
    config_match = re.search(
        r'<script type="application/json" id="admin_sortable2_config">\s*(\{.*?\})\s*</script>',
        content,
        re.S,
    )
    assert config_match is not None

    config = json.loads(config_match.group(1))
    assert config['csrf_header'] == 'X-AUTH-CSRFTOKEN'

    token_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    assert token_match is not None
    csrf_token = token_match.group(1)

    book = Book1.objects.order_by('my_order').first()
    assert book is not None

    update_payload = json.dumps({'updatedItems': [[book.pk, book.my_order]]})
    update_url = config['update_url']

    # Default header must fail when CSRF_HEADER_NAME is customized.
    default_header_response = client.post(
        update_url,
        data=update_payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert default_header_response.status_code == 403

    # Custom header succeeds and keeps the endpoint compatible with Django settings.
    custom_header_response = client.post(
        update_url,
        data=update_payload,
        content_type='application/json',
        HTTP_X_AUTH_CSRFTOKEN=csrf_token,
    )
    assert custom_header_response.status_code == 200
