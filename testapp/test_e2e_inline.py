import pytest

from testapp.models import Book


slugs = [
    'book1',  # ordered by model, stacked inlines
    'book2',  # reverse ordered by model, stacked inlines
    'book3',  # ordered by admin, stacked inlines
    'book4',  # reverse ordered by admin, stacked inlines
    'book5',  # ordered by admin, tabular inlines
    'book6',  # unsorted, sorted stacked inlines
]
js_the_good_parts_id = 17


def get_start_order(direction):
    return 1 if direction == 1 else Book.objects.get(id=js_the_good_parts_id).chapter_set.count()


def get_end_order(direction):
    return Book.objects.get(id=js_the_good_parts_id).chapter_set.count() if direction == 1 else 1


@pytest.fixture
def adminpage(live_server, page, slug):
    page.goto(f'{live_server.url}/admin/testapp/{slug}/{js_the_good_parts_id}/change/')
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
def direction(slug):
    return +1 if slug in ['book1', 'book3', 'book5', 'book6'] else -1


@pytest.fixture
def chapter(slug):
    if slug in ['book1', 'book6']:
        return '#chapter1'
    if slug in ['book2']:
        return '#chapter2'
    return '#chapter'


@pytest.mark.parametrize('slug', slugs)
def test_drag_down(adminpage, slug, direction, chapter):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    assert inline_locator.locator(f'{chapter}_set-0 input._reorder_').input_value() == str(start_order)
    drag_handle = inline_locator.locator(f'{chapter}_set-0 :is(h3, p)')
    drag_handle.drag_to(inline_locator.locator(f'{chapter}_set-4'))
    assert inline_locator.locator(f'{chapter}_set-0 input._reorder_').input_value() == str(start_order + direction * 4)
    assert inline_locator.locator(f'{chapter}_set-1 input._reorder_').input_value() == str(start_order)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)


@pytest.mark.parametrize('slug', slugs)
def test_drag_up(adminpage, slug, direction, chapter):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    reorder_field = inline_locator.locator(f'{chapter}_set-5 input._reorder_')
    assert reorder_field.input_value() == str(start_order + direction * 5)
    drag_handle = inline_locator.locator(f'{chapter}_set-5 :is(h3, p)')
    drag_handle.drag_to(inline_locator.locator(f'{chapter}_set-1'))
    assert inline_locator.locator(f'{chapter}_set-5 input._reorder_').input_value() == str(start_order + direction)
    assert inline_locator.locator(f'{chapter}_set-1 input._reorder_').input_value() == str(start_order + direction * 2)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)


@pytest.mark.parametrize('slug', ['book1', 'book2', 'book5'])
def test_move_end(adminpage, slug, direction, chapter):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    end_order = get_end_order(direction)
    assert inline_locator.locator(f'{chapter}_set-2 input._reorder_').input_value() == str(start_order + direction * 2)
    move_end_button = inline_locator.locator(f'{chapter}_set-2 :is(h3, p) .move-end').element_handle()
    move_end_button.click()
    assert inline_locator.locator(f'{chapter}_set-2 input._reorder_').input_value() == str(end_order)
    assert inline_locator.locator(f'{chapter}_set-3 input._reorder_').input_value() == str(start_order + direction * 2)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)


@pytest.mark.parametrize('slug', ['book1', 'book2', 'book5'])
def test_move_begin(adminpage, slug, direction, chapter):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
    start_order = get_start_order(direction)
    assert inline_locator.locator(f'{chapter}_set-8 input._reorder_').input_value() == str(start_order + direction * 8)
    move_end_button = inline_locator.locator(f'{chapter}_set-8 :is(h3, p) .move-begin').element_handle()
    move_end_button.click()
    assert inline_locator.locator(f'{chapter}_set-8 input._reorder_').input_value() == str(start_order)
    assert inline_locator.locator(f'{chapter}_set-3 input._reorder_').input_value() == str(start_order + direction * 4)
    assert is_fieldset_ordered(inline_locator.element_handle(), direction)
