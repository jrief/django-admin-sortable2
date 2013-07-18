# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
