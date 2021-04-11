from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^.*$', RedirectView.as_view(url='/admin/')),
]
