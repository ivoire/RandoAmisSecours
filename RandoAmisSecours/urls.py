# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2013, 2014 Rémi Duraffort
# This file is part of RandoAmisSecours.
#
# RandoAmisSecours is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RandoAmisSecours is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with RandoAmisSecours.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.auth import views as r_auth
from django.core.urlresolvers import reverse_lazy
from tastypie.api import Api

from RandoAmisSecours.api import OutingResource, ProfileResource, UserResource, GPSPointResource, LoginResource
from RandoAmisSecours.views.account import RASAuthenticationForm, RASPasswordChangeForm, RASPasswordResetForm, RASSetPasswordForm

from RandoAmisSecours.views import account as r_account
from RandoAmisSecours.views import friends as r_friends
from RandoAmisSecours.views import help as r_help
from RandoAmisSecours.views import main as r_main
from RandoAmisSecours.views import outing as r_outing
from RandoAmisSecours.views import reporting as r_reporting


# API v1.0
api_1_0 = Api(api_name='1.0')
api_1_0.register(OutingResource())
api_1_0.register(ProfileResource())
api_1_0.register(UserResource())
api_1_0.register(GPSPointResource())
api_1_0.register(LoginResource())

urlpatterns = [
    # Main page
    url(r'^$', r_main.index, name='index'),

    # Help pages
    url(r'^help/$', r_help.index, name='help.index'),
    url(r'^help/qa/$', r_help.qa, name='help.qa'),

    # Authentication
    url(r'^accounts/login/$', r_auth.login, {'template_name': 'RandoAmisSecours/account/login.html', 'authentication_form': RASAuthenticationForm}, name='accounts.login'),
    url(r'^accounts/logout/$', r_auth.logout, {'template_name': 'RandoAmisSecours/account/logged_out.html'}, name='accounts.logout'),
    url(r'^accounts/password/change/$', r_auth.password_change, {'template_name': 'RandoAmisSecours/account/password_change.html', 'password_change_form': RASPasswordChangeForm, 'post_change_redirect': reverse_lazy('accounts.password_change_done')}, name='accounts.password_change'),
    url(r'^accounts/password/reset/$', r_auth.password_reset, {'template_name': 'RandoAmisSecours/account/password_reset.html', 'email_template_name': 'RandoAmisSecours/account/password_reset_email.txt', 'password_reset_form': RASPasswordResetForm, 'post_reset_redirect': reverse_lazy('accounts.password_reset_done')}, name='accounts.password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', r_auth.password_reset_confirm, {'template_name': 'RandoAmisSecours/account/password_reset_confirm.html', 'set_password_form': RASSetPasswordForm}, name='accounts.password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', r_auth.password_reset_complete, {'template_name': 'RandoAmisSecours/account/password_reset_complete.html'}, name='password_reset_complete'),


    url(r'^accounts/register/$', r_account.register, name='accounts.register'),
    url(r'^accounts/register/(?P<user_id>\d+)/confirm/(?P<user_hash>\w+)/$', r_account.register_confirm, name='accounts.register.confirm'),
    url(r'^accounts/profile/$', r_account.profile, name='accounts.profile'),
    url(r'^accounts/profile/update/$', r_account.update, name='accounts.profile.update'),
    url(r'^accounts/password/change/done/$', r_account.password_change_done, name='accounts.password_change_done'),
    url(r'^accounts/password/reset/done/$', r_account.password_reset_done, name='accounts.password_reset_done'),
    url(r'^accounts/delete/$', r_account.delete, name='accounts.delete'),

    # Friends
    url(r'^friends/search/$', r_friends.search, name='friends.search'),
    url(r'^friends/invite/(?P<user_id>\d+)/$', r_friends.invite, name='friends.invite'),
    url(r'^friends/accept/(?P<request_id>\d+)/$', r_friends.accept, name='friends.accept'),
    url(r'^friends/refuse/(?P<request_id>\d+)/$', r_friends.refuse, name='friends.refuse'),
    url(r'^friends/cancel/(?P<request_id>\d+)/$', r_friends.cancel, name='friends.cancel'),
    url(r'^friends/delete/(?P<user_id>\d+)/$', r_friends.delete, name='friends.delete'),

    # Outings
    url(r'^outings/$', r_outing.index, name='outings.index'),
    url(r'^outings/create/$', r_outing.create, name='outings.create'),
    url(r'^outings/(?P<outing_id>\d+)/$', r_outing.details, name='outings.details'),
    url(r'^outings/(?P<outing_id>\d+)/trace/$', r_outing.details_trace, name='outings.details.trace'),
    url(r'^outings/(?P<outing_id>\d+)/update/$', r_outing.update, name='outings.update'),
    url(r'^outings/(?P<outing_id>\d+)/delete/$', r_outing.delete, name='outings.delete'),
    url(r'^outings/(?P<outing_id>\d+)/confirm/$', r_outing.confirm, name='outings.confirm'),
    url(r'^outings/(?P<outing_id>\d+)/finish/$', r_outing.finish, name='outings.finish'),

    # Reporting
    url(r'^reporting/$', r_reporting.index, name='reporting.index'),
    url(r'^reporting/users/$', r_reporting.users, name='reporting.users'),
    url(r'^reporting/outings/late/$', r_reporting.outings_late, name='reporting.outings.late'),

    # API
    url(r'^api/', include(api_1_0.urls)),
]
