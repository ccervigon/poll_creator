# -*- coding: utf-8 -*- 

from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'surveyApp.views.welcome', name='welcome'),
    url(r'^survey2$', 'surveyApp.views.survey2', name='survey2'),
    url(r'^survey$', 'surveyApp.views.survey', name='survey'),
    url(r'^thanks$', 'surveyApp.views.thanks', name='thanks'),
    url(r'^result$', 'surveyApp.views.result', name='result'),
    url(r'^info$', 'surveyApp.views.information', name='information'),
    url(r'^privacy$', 'surveyApp.views.privacy', name='privacy'),
    url(r'^contact$', 'surveyApp.views.contact', name='contact'),
    url(r'^(?P<author_hash>\w+)', 'surveyApp.views.welcome', name='welcome'),

    url(r'^admin/', include(admin.site.urls)),
)
