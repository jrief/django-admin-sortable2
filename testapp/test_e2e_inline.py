import pytest

from django.urls import reverse


@pytest.fixture
def page(connector):
    url = reverse('admin:testapp_sortablebook1_change', args=(17,))
    connector.page.goto(f'{connector.live_server.url}{url}')
    return connector.page


def is_fieldset_ordered(inline_elem):
    for counter, order_field in enumerate(inline_elem.query_selector_all('div.inline-related.has_original > fieldset > .field-my_order input._reorder_'), 1):
        if order_field.input_value() != str(counter):
            return False
    return True


def test_drag_down(page):
    inline_locator = page.locator('#chapter_set-group')
    inline_element = inline_locator.element_handle()
    assert is_fieldset_ordered(inline_element)
    assert inline_element.query_selector('#chapter_set-0 input._reorder_').input_value() == '1'
    drag_handle = inline_locator.locator('#chapter_set-0 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-4'))
    assert inline_element.query_selector('#chapter_set-0 input._reorder_').input_value() == '5'
    assert inline_element.query_selector('#chapter_set-1 input._reorder_').input_value() == '1'
    assert is_fieldset_ordered(inline_element)


def test_drag_up(page):
    inline_locator = page.locator('#chapter_set-group')
    inline_element = inline_locator.element_handle()
    assert is_fieldset_ordered(inline_element)
    assert inline_element.query_selector('#chapter_set-5 input._reorder_').input_value() == '6'
    drag_handle = inline_locator.locator('#chapter_set-5 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-1'))
    assert inline_element.query_selector('#chapter_set-5 input._reorder_').input_value() == '2'
    assert inline_element.query_selector('#chapter_set-1 input._reorder_').input_value() == '3'
    assert is_fieldset_ordered(inline_element)
