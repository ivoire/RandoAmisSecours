# -*- coding: utf-8 -*-
# vim: set ts=4

from django.conf.urls import patterns, url

urlpatterns = patterns('RandoAmisSecours.views.main',
    url(r'^$', 'index', name='index')
)
