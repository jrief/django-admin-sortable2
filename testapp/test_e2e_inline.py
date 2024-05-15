import pytest
from time import sleep
from playwright.sync_api import expect

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
    url = f'{live_server.url}/admin/testapp/{slug}/{js_the_good_parts_id}/change/'
    page.goto(url)
    return page


def expect_fieldset_is_ordered(inline_elem, direction):
    expect(inline_elem).to_be_visible()
    start_order = get_start_order(direction)
    inline_related = inline_elem.locator('div.inline-related.has_original')
    for counter in range(inline_related.count()):
        row = inline_related.nth(counter)
        order_field = row.locator('fieldset input._reorder_')
        expect(order_field).to_be_hidden()
        order = start_order + direction * counter
        expect(order_field).to_have_value(str(order))


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


@pytest.fixture
def drag_selector(slug):
    if slug in ['book5']:
        return '> td > p'
    return '> h3'


@pytest.mark.parametrize('slug', slugs)
def test_drag_down(adminpage, slug, direction, chapter, drag_selector):
    group_locator = adminpage.locator(f'{chapter}_set-group')
    expect_fieldset_is_ordered(group_locator, direction)
    start_order = get_start_order(direction)
    expect(group_locator.locator(f'{chapter}_set-0 input._reorder_')).to_have_value(str(start_order))
    drag_kwargs = {'source_position': {'x': 190, 'y': 9}, 'target_position': {'x': 200, 'y': 10}}
    drag_handle = group_locator.locator(f'{chapter}_set-0 {drag_selector}')
    expect(drag_handle).to_be_visible()
    drag_handle.drag_to(group_locator.locator(f'{chapter}_set-3'), **drag_kwargs)
    sleep(0.3)  # sortablejs needs some time to update the order
    expect(group_locator.locator(f'{chapter}_set-0 input._reorder_')).to_have_value(str(start_order + direction * 3))
    expect(group_locator.locator(f'{chapter}_set-1 input._reorder_')).to_have_value(str(start_order))
    expect_fieldset_is_ordered(group_locator, direction)


@pytest.mark.parametrize('slug', slugs)
def test_drag_up(adminpage, slug, direction, chapter, drag_selector):
    group_locator = adminpage.locator(f'{chapter}_set-group')
    expect_fieldset_is_ordered(group_locator, direction)
    start_order = get_start_order(direction)
    expect(group_locator.locator(f'{chapter}_set-5 input._reorder_')).to_have_value(str(start_order + direction * 5))
    drag_kwargs = {'source_position': {'x': 200, 'y': 10}, 'target_position': {'x': 200, 'y': 10}}
    drag_handle = group_locator.locator(f'{chapter}_set-5 {drag_selector}')
    drag_handle.drag_to(group_locator.locator(f'{chapter}_set-1'), **drag_kwargs)
    expect(group_locator.locator(f'{chapter}_set-5 input._reorder_')).to_have_value(str(start_order + direction))
    expect(group_locator.locator(f'{chapter}_set-1 input._reorder_')).to_have_value(str(start_order + direction * 2))
    expect_fieldset_is_ordered(group_locator, direction)


@pytest.mark.parametrize('slug', ['book1', 'book2', 'book5'])
def test_move_end(adminpage, slug, direction, chapter, drag_selector):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    expect_fieldset_is_ordered(inline_locator, direction)
    start_order = get_start_order(direction)
    end_order = get_end_order(direction)
    expect(inline_locator.locator(f'{chapter}_set-2 input._reorder_')).to_have_value(str(start_order + direction * 2))
    move_end_button = inline_locator.locator(f'{chapter}_set-2 {drag_selector} .move-end').element_handle()
    move_end_button.click()
    expect(inline_locator.locator(f'{chapter}_set-2 input._reorder_')).to_have_value(str(end_order))
    expect(inline_locator.locator(f'{chapter}_set-3 input._reorder_')).to_have_value(str(start_order + direction * 2))
    expect_fieldset_is_ordered(inline_locator, direction)


@pytest.mark.parametrize('slug', ['book1', 'book2', 'book5'])
def test_move_begin(adminpage, slug, direction, chapter, drag_selector):
    inline_locator = adminpage.locator(f'{chapter}_set-group')
    expect_fieldset_is_ordered(inline_locator, direction)
    start_order = get_start_order(direction)
    expect(inline_locator.locator(f'{chapter}_set-8 input._reorder_')).to_have_value(str(start_order + direction * 8))
    move_end_button = inline_locator.locator(f'{chapter}_set-8 {drag_selector} .move-begin')
    move_end_button.click()
    expect(inline_locator.locator(f'{chapter}_set-8 input._reorder_')).to_have_value(str(start_order))
    expect(inline_locator.locator(f'{chapter}_set-3 input._reorder_')).to_have_value(str(start_order + direction * 4))
    expect_fieldset_is_ordered(inline_locator, direction)
