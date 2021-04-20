from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^.*$', RedirectView.as_view(url='/admin/')),
]
