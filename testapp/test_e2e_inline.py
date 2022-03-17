import pytest

from django.urls import reverse


@pytest.fixture
def page(live_server, page):
    url = reverse('admin:testapp_sortablebook1_change', args=(17,))
    page.goto(f'{live_server.url}{url}')
    return page


def is_fieldset_ordered(inline_elem):
    for counter, row in enumerate(inline_elem.query_selector_all('div.inline-related.has_original'), 1):
        order_field = row.query_selector('fieldset input._reorder_')
        assert order_field is not None
        if order_field.input_value() != str(counter):
            return False
    return True


def test_drag_down(page):
    inline_locator = page.locator('#chapter_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle())
    assert inline_locator.locator('#chapter_set-0 input._reorder_').input_value() == '1'
    drag_handle = inline_locator.locator('#chapter_set-0 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-4'))
    assert inline_locator.locator('#chapter_set-0 input._reorder_').input_value() == '5'
    assert inline_locator.locator('#chapter_set-1 input._reorder_').input_value() == '1'
    assert is_fieldset_ordered(inline_locator.element_handle())


def test_drag_up(page):
    inline_locator = page.locator('#chapter_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle())
    reorder_field = inline_locator.locator('#chapter_set-5 input._reorder_')
    assert reorder_field.input_value() == '6'
    drag_handle = inline_locator.locator('#chapter_set-5 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-1'))
    assert inline_locator.locator('#chapter_set-5 input._reorder_').input_value() == '2'
    assert inline_locator.locator('#chapter_set-1 input._reorder_').input_value() == '3'
    assert is_fieldset_ordered(inline_locator.element_handle())
