import warnings

import pytest

from django.test import Client
from django.urls import reverse

try:
    from django.contrib.admin import ActionLocation
    from django.utils.deprecation import RemovedInDjango2028Warning
except ImportError:  # Django < 6.1
    ActionLocation = RemovedInDjango2028Warning = None

requires_action_location = pytest.mark.skipif(
    ActionLocation is None,
    reason="ModelAdmin.get_actions() takes action_location since Django 6.1",
)

move_actions = {
    'move_to_first_page',
    'move_to_back_page',
    'move_to_forward_page',
    'move_to_last_page',
    'move_to_exact_page',
}


@requires_action_location
@pytest.mark.django_db
def test_changelist_get_actions_not_deprecated():
    client = Client()
    with warnings.catch_warnings():
        warnings.simplefilter('error', RemovedInDjango2028Warning)
        response = client.get(reverse('admin:testapp_book0_changelist'), {'p': 2})
    assert response.status_code == 200
    assert b'move_to_first_page' in response.content


@requires_action_location
@pytest.mark.django_db
def test_change_form_get_actions_without_move_actions():
    response = Client().get(reverse('admin:testapp_book0_changelist'), {'p': 2})
    model_admin, request = response.context_data['cl'].model_admin, response.wsgi_request
    assert 'move_to_first_page' in model_admin.get_actions(request, action_location=ActionLocation.CHANGE_LIST)
    assert not move_actions & set(model_admin.get_actions(request, action_location=ActionLocation.CHANGE_FORM))
