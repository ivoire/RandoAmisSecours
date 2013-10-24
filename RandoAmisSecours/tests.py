# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2013 Rémi Duraffort
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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import datetime, utc

from RandoAmisSecours.models import Outing, Profile


class TemplatesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('azertyuiop',
                                             'django.test@project.org',
                                             '12789azertyuiop')
        self.client.login(username='azertyuiop', password='12789azertyuiop')
        self.user.profile = Profile.objects.create(user=self.user)

    def helper_template(self, url, template):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertEqual(response.templates[0].name, "RandoAmisSecours/%s" % (template))
        self.assertEqual(response.templates[1].name, 'RandoAmisSecours/base.html')

    def test_main(self):
        self.helper_template(reverse('index'), 'main/index.html')

    def test_help(self):
        self.helper_template(reverse('help.index'), 'help/index.html')
        self.helper_template(reverse('help.qa'), 'help/qa.html')

    def test_auth(self):
        self.helper_template(reverse('accounts.password_change'), 'account/password_change.html')
        self.helper_template(reverse('accounts.password_reset'), 'account/password_reset.html')
        self.helper_template(reverse('accounts.password_reset_confirm', args=[1,'1-1']), 'account/password_reset_confirm.html')
        self.helper_template(reverse('accounts.password_reset_complete'), 'account/password_reset_complete.html')
        self.helper_template(reverse('accounts.logout'), 'account/logged_out.html')
        self.helper_template(reverse('accounts.login'), 'account/login.html')

    def test_profile(self):
        self.helper_template(reverse('accounts.register'), 'account/register.html')
        self.helper_template(reverse('accounts.register.confirm', args=[1, self.user.profile.hash_id]), 'account/confirm.html')
        self.helper_template(reverse('accounts.profile'), 'account/profile.html')
        self.helper_template(reverse('accounts.profile.update'), 'account/update.html')
        self.helper_template(reverse('accounts.password_reset_done'), 'account/password_reset_done.html')

    def test_friends(self):
        self.helper_template(reverse('friends.search'), 'friends/search.html')

    def test_outings(self):
        self.helper_template(reverse('outings.index'), 'outing/index.html')
        self.helper_template(reverse('outings.index.draft'), 'outing/index.html')
        self.helper_template(reverse('outings.index.finished'), 'outing/index.html')
        self.helper_template(reverse('outings.index.late'), 'outing/index.html')
        self.helper_template(reverse('outings.index.canceled'), 'outing/index.html')
        self.helper_template(reverse('outings.create'), 'outing/create.html')

        current_time = datetime.utcnow().replace(tzinfo=utc)
        outing = Outing.objects.create(user=self.user, beginning=current_time,
                                       ending=current_time, alert=current_time,
                                       latitude=1, longitude=1)
        self.helper_template(reverse('outings.update', args=[outing.pk]), 'outing/create.html')
