# -*- coding: utf-8 -*- 

from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'pollApp.views.welcome', name='welcome'),
    url(r'^poll', 'pollApp.views.poll', name='poll'),
    url(r'^thanks', 'pollApp.views.thanks', name='thanks'),
    url(r'^(?P<email_hash>\w+)$', 'pollApp.views.welcome', name='welcome'),

    url(r'^admin/', include(admin.site.urls)),
)
