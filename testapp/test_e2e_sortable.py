import pytest
from time import sleep

from django import VERSION as DJANGO_VERSION
from django.urls import reverse

from testapp.models import SortableBook


@pytest.fixture(scope='function')
def django_db_setup(django_db_blocker):
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)
        call_command('loaddata', 'testapp/fixtures/data.json', verbosity=0)


page_3 = 3 if DJANGO_VERSION >= (3, 0) else 2
viewnames = [
    ('admin:testapp_sortablebook1_changelist', None, None),
    ('admin:testapp_sortablebook1_changelist', None, 3),
    ('admin:testapp_sortablebook1_changelist', None, -3),
    ('admin:testapp_sortablebook1_changelist', page_3, None),
    ('admin:testapp_sortablebook1_changelist', page_3, -3),
    ('admin:testapp_sortablebook1_changelist', None, 2),
    ('admin:testapp_sortablebook2_changelist', None, None),
    ('admin:testapp_sortablebook2_changelist', None, 3),
    ('admin:testapp_sortablebook2_changelist', None, -3),
    ('admin:testapp_sortablebook3_changelist', None, None),
    ('admin:testapp_sortablebook3_changelist', None, 3),
    ('admin:testapp_sortablebook3_changelist', None, -3),
    ('admin:testapp_sortablebook4_changelist', None, None),
]


def is_table_ordered(table_elem, page=None, direction=1):
    if page is None:
        page = 0
    elif DJANGO_VERSION >= (3, 0):
        page -= 1
    if direction == 1:
        start_order = 12 * page + 1
    else:
        start_order = SortableBook.objects.count() - 12 * page
    for counter, row in enumerate(table_elem.query_selector_all('tbody tr')):
        drag_handle = row.query_selector('div.drag')
        order = start_order + direction * counter
        if drag_handle.get_attribute('order') != str(order):
            return False
    return True


@pytest.fixture
def direction(viewname, o):
    if o is None:
        return +1 if viewname in ['admin:testapp_sortablebook1_changelist', 'admin:testapp_sortablebook3_changelist'] else -1
    return +1 if o > 0 else -1


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_to_end(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    drag_handle = table_locator.locator('tbody tr:nth-of-type(5) div.drag')
    if o == 2:
        assert not is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
        assert 'handle' not in drag_handle.get_attribute('class')
        return
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    drag_row_pk = drag_handle.get_attribute('pk')
    next_row_pk = table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')
    update_url = viewname.replace('_changelist', '_sortable_update')
    with page.expect_response(reverse(update_url)) as response_info:
        drag_handle.drag_to(table_locator.locator('tbody tr:last-of-type'))
    while not response_info.is_done():
        sleep(0.1)
    response = response_info.value
    assert response.ok
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:last-of-type div.drag.handle').get_attribute('pk')
    assert next_row_pk == table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_down(page, viewname, p, o, direction):
    if o == 2:
        return
    table_locator = page.locator('table#result_list')
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(4) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    next_row_pk = table_locator.locator('tbody tr:nth-of-type(7) div.drag.handle').get_attribute('pk')
    update_url = viewname.replace('_changelist', '_sortable_update')
    with page.expect_response(reverse(update_url)) as response_info:
        drag_handle.drag_to(table_locator.locator('tbody tr:nth-of-type(9)'))
    while not response_info.is_done():
        sleep(0.1)
    response = response_info.value
    assert response.ok
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:nth-of-type(9) div.drag.handle').get_attribute('pk')
    assert next_row_pk == table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_to_start(page, viewname, p, o, direction):
    if o == 2:
        return
    table_locator = page.locator('table#result_list')
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    prev_row_pk = table_locator.locator('tbody tr:nth-of-type(4) div.drag.handle').get_attribute('pk')
    update_url = viewname.replace('_changelist', '_sortable_update')
    with page.expect_response(reverse(update_url)) as response_info:
        drag_handle.drag_to(table_locator.locator('tbody tr:first-of-type'))
    while not response_info.is_done():
        sleep(0.1)
    response = response_info.value
    assert response.ok
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:first-of-type div.drag.handle').get_attribute('pk')
    assert prev_row_pk == table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_up(page, viewname, p, o, direction):
    if o == 2:
        return
    table_locator = page.locator('table#result_list')
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(9) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    prev_row_pk = table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')
    update_url = viewname.replace('_changelist', '_sortable_update')
    with page.expect_response(reverse(update_url)) as response_info:
        drag_handle.drag_to(table_locator.locator('tbody tr:nth-of-type(3)'))
    while not response_info.is_done():
        sleep(0.1)
    response = response_info.value
    assert response.ok
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:nth-of-type(3) div.drag.handle').get_attribute('pk')
    assert prev_row_pk == table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', [
    ('admin:testapp_sortablebook1_changelist', None, None),
    ('admin:testapp_sortablebook2_changelist', None, -3),
    ('admin:testapp_sortablebook4_changelist', None, None),
])
def test_move_next_page(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    book_attributes = []
    for n in range(2, 7, 2):
        book_attributes.append((
            int(table_locator.locator(f'tbody tr:nth-of-type({n}) div.drag.handle').element_handle().get_attribute('pk')),
            int(table_locator.locator(f'tbody tr:nth-of-type({n}) div.drag.handle').element_handle().get_attribute('order')),
        ))
        table_locator.locator(f'tbody tr:nth-of-type({n}) input.action-select').click()
    step_input_field = page.query_selector('#changelist-form .actions input[name="step"]')
    assert step_input_field.is_hidden()
    page.query_selector('#changelist-form .actions select[name="action"]').select_option('move_to_forward_page')
    assert step_input_field.is_visible()
    step_input_field.focus()
    page.keyboard.press("Delete")
    step_input_field.type("2")
    with page.expect_response(page.url) as response_info:
        page.query_selector('#changelist-form .actions button[type="submit"]').click()
    while not response_info.is_done():
        sleep(0.1)
    response = response_info.value
    assert response.status == 302
    assert response.url == page.url
    assert is_table_ordered(table_locator.element_handle(), page=p, direction=direction)
    for index, (pk, order) in enumerate(book_attributes):
        book = SortableBook.objects.get(pk=pk)
        if direction > 0:
            assert book.my_order == 25 + index
        else:
            assert book.my_order == SortableBook.objects.count() - 24 - index
