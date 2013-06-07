# -*- coding: utf-8 -*-
# vim: set ts=4

from django.conf.urls import patterns, url

# Main page
urlpatterns = patterns('RandoAmisSecours.views.main',
    url(r'^$', 'index', name='index'),
)

# Authentication
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login$', 'login', {'template_name': 'RandoAmisSecours/account/login.html'}, name='accounts.login'),
    url(r'^accounts/logout$', 'logout', {'template_name': 'RandoAmisSecours/account/logged_out.html'}, name='accounts.logout'),
)

urlpatterns += patterns('RandoAmisSecours.views.profile',
    url(r'^accounts/profile$', 'profile', name='accounts.profile'),
)

# Outing
urlpatterns += patterns('RandoAmisSecours.views.outing',
    url(r'^outings$', 'index', name='outings.index'),
    url(r'^outings/draft$', 'index', {'status': 'draft'}, name='outings.index.draft'),
    url(r'^outings/finished$', 'index', {'status': 'finished'}, name='outings.index.finished'),
    url(r'^outings/late$', 'index', {'status': 'late'}, name='outings.index.late'),
    url(r'^outings/canceled$', 'index', {'status': 'canceled'}, name='outings.index.canceled'),
    url(r'^outings/(?P<outing_id>\d+)$', 'details', name='outings.details'),
)
