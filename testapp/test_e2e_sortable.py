from time import sleep
import pytest

from testapp.models import SortableBook


@pytest.fixture(scope='function')
def django_db_setup(django_db_blocker):
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)
        call_command('loaddata', 'testapp/fixtures/data.json', verbosity=0)


viewnames = [
    ('admin:testapp_sortablebook1_changelist', None, None),
    ('admin:testapp_sortablebook1_changelist', None, 3),
    ('admin:testapp_sortablebook1_changelist', None, -3),
    ('admin:testapp_sortablebook1_changelist', 3, None),
    ('admin:testapp_sortablebook1_changelist', 3, -3),
    ('admin:testapp_sortablebook2_changelist', None, None),
    ('admin:testapp_sortablebook2_changelist', None, 3),
    ('admin:testapp_sortablebook2_changelist', None, -3),
    ('admin:testapp_sortablebook3_changelist', None, None),
    ('admin:testapp_sortablebook3_changelist', None, 3),
    ('admin:testapp_sortablebook3_changelist', None, -3),
    ('admin:testapp_sortablebook4_changelist', None, None),
]


def check_table_order(table_elem, page=None, direction=1):
    page = 1 if page is None else page
    if direction == 1:
        start_order = 12 * (page - 1) + 1
    else:
        start_order = SortableBook.objects.count() - 12 * (page - 1)
    for counter, row in enumerate(table_elem.query_selector_all('tbody tr')):
        drag_handle = row.query_selector('div.drag.handle')
        order = start_order + direction * counter
        assert drag_handle.get_attribute('order') == str(order)


@pytest.fixture
def direction(viewname, o):
    o = +1 if o is None or o > 0 else -1
    d = +1 if viewname in ['admin:testapp_sortablebook1_changelist', 'admin:testapp_sortablebook3_changelist'] else -1
    return d * o


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_to_end(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    next_row_pk = table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')
    drag_handle.drag_to(table_locator.locator('tbody tr:last-of-type'))
    sleep(0.2)
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:last-of-type div.drag.handle').get_attribute('pk')
    assert next_row_pk == table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_down(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(4) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    next_row_pk = table_locator.locator('tbody tr:nth-of-type(7) div.drag.handle').get_attribute('pk')
    drag_handle.drag_to(table_locator.locator('tbody tr:nth-of-type(9)'))
    sleep(0.2)
    path = f"{viewname.replace(':', '_')}.png"
    page.screenshot(path=path)
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:nth-of-type(9) div.drag.handle').get_attribute('pk')
    assert next_row_pk == table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_to_start(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    prev_row_pk = table_locator.locator('tbody tr:nth-of-type(4) div.drag.handle').get_attribute('pk')
    drag_handle.drag_to(table_locator.locator('tbody tr:first-of-type'))
    sleep(0.2)
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:first-of-type div.drag.handle').get_attribute('pk')
    assert prev_row_pk == table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')


@pytest.mark.parametrize('viewname, p, o', viewnames)
def test_drag_up(page, viewname, p, o, direction):
    table_locator = page.locator('table#result_list')
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    drag_handle = table_locator.locator('tbody tr:nth-of-type(9) div.drag.handle')
    drag_row_pk = drag_handle.get_attribute('pk')
    prev_row_pk = table_locator.locator('tbody tr:nth-of-type(5) div.drag.handle').get_attribute('pk')
    drag_handle.drag_to(table_locator.locator('tbody tr:nth-of-type(3)'))
    sleep(0.2)
    check_table_order(table_locator.element_handle(), page=p, direction=direction)
    assert drag_row_pk == table_locator.locator('tbody tr:nth-of-type(3) div.drag.handle').get_attribute('pk')
    assert prev_row_pk == table_locator.locator('tbody tr:nth-of-type(6) div.drag.handle').get_attribute('pk')
