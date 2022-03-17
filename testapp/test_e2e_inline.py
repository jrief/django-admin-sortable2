import pytest

from django.urls import reverse

from testapp.models import SortableBook


viewnames = [
    'admin:testapp_sortablebook1_change',
    'admin:testapp_sortablebook2_change',
]
the_good_parts_id = 17


def get_start_order(direction):
    return 1 if direction == 1 else SortableBook.objects.get(id=the_good_parts_id).chapter_set.count()


@pytest.fixture
def page(live_server, page, viewname):
    url = reverse(viewname, args=(the_good_parts_id,))
    page.goto(f'{live_server.url}{url}')
    return page


def is_fieldset_ordered(inline_elem, direction):
    start_order = get_start_order(direction)
    for counter, row in enumerate(inline_elem.query_selector_all('div.inline-related.has_original')):
        order_field = row.query_selector('fieldset input._reorder_')
        assert order_field is not None
        order = start_order + direction * counter
        if order_field.input_value() != str(order):
            return False
    return True


@pytest.fixture
def direction(viewname):
    return +1 if viewname in ['admin:testapp_sortablebook1_change'] else -1


@pytest.mark.parametrize('viewname', viewnames)
def test_drag_down(page, viewname, direction):
    inline_locator = page.locator('#chapter_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    assert inline_locator.locator('#chapter_set-0 input._reorder_').input_value() == str(start_order)
    drag_handle = inline_locator.locator('#chapter_set-0 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-4'))
    assert inline_locator.locator('#chapter_set-0 input._reorder_').input_value() == str(start_order + direction * 4)
    assert inline_locator.locator('#chapter_set-1 input._reorder_').input_value() == str(start_order)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)


@pytest.mark.parametrize('viewname', viewnames)
def test_drag_up(page, viewname, direction):
    inline_locator = page.locator('#chapter_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    reorder_field = inline_locator.locator('#chapter_set-5 input._reorder_')
    assert reorder_field.input_value() == str(start_order + direction * 5)
    drag_handle = inline_locator.locator('#chapter_set-5 > h3')
    drag_handle.drag_to(inline_locator.locator('#chapter_set-1'))
    assert inline_locator.locator('#chapter_set-5 input._reorder_').input_value() == str(start_order + direction)
    assert inline_locator.locator('#chapter_set-1 input._reorder_').input_value() == str(start_order + direction * 2)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
