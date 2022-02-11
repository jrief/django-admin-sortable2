import pytest


@pytest.fixture(scope='function')
def django_db_setup(django_db_blocker):
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)
        call_command('loaddata', 'testapp/fixtures/data.json', verbosity=0)


viewnames = [
    'admin:testapp_sortablebook_changelist',  # ModelAdmin orders up
    'admin:testapp_unorderedsortablebook_changelist',  # ModelAdmin orders down
    'admin:testapp_uporderedsortablebook_changelist',  # Model orders up
    'admin:testapp_downorderedsortablebook_changelist',  # Model orders down
]


@pytest.mark.parametrize('viewname', viewnames)
def test_list_view(page, viewname):
    path = f"{viewname.replace(':', '_')}.png"
    page.screenshot(path=path)
    assert True
