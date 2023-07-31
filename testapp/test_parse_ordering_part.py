from django.db.models import F, OrderBy

# noinspection PyProtectedMember
from adminsortable2.admin import _parse_ordering_part as parse


def test():
    assert parse('my_order')                               == ('', 'my_order')
    assert parse(F('my_order'))                            == ('', 'my_order')
    assert parse(F('my_order').asc())                      == ('', 'my_order')
    assert parse(OrderBy(F('my_order')))                   == ('', 'my_order')
    assert parse(OrderBy(F('my_order'), descending=False)) == ('', 'my_order')

    assert parse('-my_order')                             == ('-', 'my_order')
    assert parse(F('my_order').desc())                    == ('-', 'my_order')
    assert parse(OrderBy(F('my_order'), descending=True)) == ('-', 'my_order')

    assert parse(F("foo") + F("bar")) == ('', None)
