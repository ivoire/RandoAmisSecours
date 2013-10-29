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

from RandoAmisSecours.models import FriendRequest, Outing, Profile
from RandoAmisSecours.models import CONFIRMED, DRAFT, FINISHED


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
        self.helper_template(reverse('accounts.password_reset_confirm', args=[1, '1-1']), 'account/password_reset_confirm.html')
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
        self.helper_template(reverse('outings.create'), 'outing/create.html')

        current_time = datetime.utcnow().replace(tzinfo=utc)
        outing = Outing.objects.create(user=self.user, beginning=current_time,
                                       ending=current_time, alert=current_time,
                                       latitude=1, longitude=1)
        self.helper_template(reverse('outings.update', args=[outing.pk]), 'outing/create.html')


class LoginRequired(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('azertyuiop',
                                             'django.test@project.org',
                                             '12789azertyuiop')
        self.user.profile = Profile.objects.create(user=self.user)
        self.user2 = User.objects.create_user('zarterzh',
                                             'gzeryztye@example.org',
                                             'help')
        self.user2.profile = Profile.objects.create(user=self.user2)

        current_time = datetime.utcnow().replace(tzinfo=utc)
        self.outing = Outing.objects.create(user=self.user, beginning=current_time,
                                            ending=current_time, alert=current_time,
                                            latitude=1, longitude=1)

    def helper_test_login(self, url, redirect=None):
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, "%s?next=%s" % (reverse('accounts.login'), url))

        self.client.login(username='azertyuiop', password='12789azertyuiop')
        response = self.client.get(url)
        if redirect:
            self.assertRedirects(response, redirect)
        else:
            self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_account(self):
        self.helper_test_login(reverse('accounts.password_change'))
        self.helper_test_login(reverse('accounts.profile'))
        self.helper_test_login(reverse('accounts.profile.update'))
        self.helper_test_login(reverse('accounts.password_change_done'), redirect=reverse('accounts.profile'))

    def test_friends(self):
        self.helper_test_login(reverse('friends.search'))

        self.helper_test_login(reverse('friends.invite', args=[self.user2.pk]), redirect=reverse('friends.search'))
        FriendRequest.objects.all().delete()
        FR = FriendRequest(user=self.user2, to=self.user)
        FR.save()
        self.helper_test_login(reverse('friends.accept', args=[FR.pk]), redirect=reverse('accounts.profile'))
        self.helper_test_login(reverse('friends.delete', args=[self.user2.pk]), redirect=reverse('accounts.profile'))

        FR = FriendRequest(user=self.user2, to=self.user)
        FR.save()
        self.helper_test_login(reverse('friends.refuse', args=[FR.pk]), redirect=reverse('accounts.profile'))

        self.helper_test_login(reverse('friends.invite', args=[self.user2.pk]), redirect=reverse('friends.search'))
        self.helper_test_login(reverse('friends.cancel', args=[FriendRequest.objects.all()[0].pk]), redirect=reverse('accounts.profile'))

    def test_outings(self):
        self.helper_test_login(reverse('outings.index'))
        self.helper_test_login(reverse('outings.create'))

        self.helper_test_login(reverse('outings.details', args=[self.outing.pk]))
        self.helper_test_login(reverse('outings.update', args=[self.outing.pk]))
        self.helper_test_login(reverse('outings.confirm', args=[self.outing.pk]), redirect=reverse('outings.index'))
        self.helper_test_login(reverse('outings.finish', args=[self.outing.pk]), redirect=reverse('outings.index'))
        self.helper_test_login(reverse('outings.delete', args=[self.outing.pk]), redirect=reverse('outings.index'))


class FriendsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('ras',
                                              'ras@project.org',
                                              '12789azertyuiop')
        self.user1.first_name = 'Rando'
        self.user1.last_name = 'Secours'
        self.user1.save()
        self.user1.profile = Profile.objects.create(user=self.user1)
        self.client.login(username='ras', password='12789azertyuiop')

        self.user2 = User.objects.create_user('tester',
                                              'tester@project.org',
                                              'ertyfjnbfvfceqsryuj')
        self.user2.first_name = 'Alpha'
        self.user2.last_name = 'Beta Gamma'
        self.user2.save()
        self.user2.profile = Profile.objects.create(user=self.user2)

        self.user3 = User.objects.create_user('Sophocle',
                                              'sophocle@project.org',
                                              'gzgvaryurvyyjchrvyhubtr')
        self.user3.first_name = 'Sophocle'
        self.user3.last_name = 'Philosophe'
        self.user3.save()
        self.user3.profile = Profile.objects.create(user=self.user3)

    # Compare Friend requests
    def helper_compare_FR(self, fr, user, to):
        self.assertEqual(fr.user, user)
        self.assertEqual(fr.to, to)

    def test_search(self):
        # Empty without query
        response = self.client.get(reverse('friends.search'))
        ctx = response.context
        self.assertEqual(ctx['query'], None)
        self.assertEqual(ctx['results'], None)

        # An empty query
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), ''))
        ctx = response.context
        self.assertEqual(ctx['query'], u'')
        self.assertEqual(ctx['results'], None)

        # Match on queries
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'sop'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'sop')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user3.profile)

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'Sopho'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'Sopho')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user3.profile)

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'S'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'S')
        self.assertEqual(len(ctx['results']), 2)
        self.assertEqual(ctx['results'][0], self.user2.profile)
        self.assertEqual(ctx['results'][1], self.user3.profile)

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'alpha'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'alpha')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user2.profile)

        # Does not match the requester
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'ras'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'ras')
        self.assertEqual(len(ctx['results']), 0)

        # match the emails
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'project.org'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'project.org')
        self.assertEqual(len(ctx['results']), 2)
        self.assertEqual(ctx['results'][0], self.user2.profile)
        self.assertEqual(ctx['results'][1], self.user3.profile)

        # Change the logged-in user
        self.client.login(username='tester', password='ertyfjnbfvfceqsryuj')
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'S'))
        ctx = response.context
        self.assertEqual(ctx['query'], u'S')
        self.assertEqual(len(ctx['results']), 2)
        self.assertEqual(ctx['results'][0], self.user1.profile)
        self.assertEqual(ctx['results'][1], self.user3.profile)

    def test_invite(self):
        response = self.client.get(reverse('friends.invite', args=[self.user1.profile.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('friends.invite', args=[self.user2.profile.pk]))
        self.assertRedirects(response, reverse('friends.search'))
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.helper_compare_FR(FriendRequest.objects.all()[0], user=self.user1, to=self.user2)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.invite', args=[self.user3.profile.pk]))
        self.assertRedirects(response, reverse('friends.search'))
        self.assertEqual(FriendRequest.objects.all().count(), 2)
        self.helper_compare_FR(FriendRequest.objects.all()[0], user=self.user1, to=self.user2)
        self.helper_compare_FR(FriendRequest.objects.all()[1], user=self.user1, to=self.user3)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

    def test_accept_simple(self):
        # Simple accept session
        FR = FriendRequest(user=self.user2, to=self.user1)
        FR.save()
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.accept', args=[FR.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(FriendRequest.objects.all().count(), 0)
        self.assertEqual(self.user1.profile.friends.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all()[0].user.pk, self.user2.pk)
        self.assertEqual(self.user2.profile.friends.all().count(), 1)
        self.assertEqual(self.user2.profile.friends.all()[0].user.pk, self.user1.pk)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

    def test_accept_advance(self):
        # Two at a time
        FR1 = FriendRequest(user=self.user3, to=self.user1)
        FR1.save()
        FR2 = FriendRequest(user=self.user2, to=self.user1)
        FR2.save()
        self.assertEqual(FriendRequest.objects.all().count(), 2)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.accept', args=[FR2.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all()[0].user.pk, self.user2.pk)
        self.assertEqual(self.user2.profile.friends.all().count(), 1)
        self.assertEqual(self.user2.profile.friends.all()[0].user.pk, self.user1.pk)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.accept', args=[FR2.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('friends.accept', args=[FR1.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(FriendRequest.objects.all().count(), 0)
        self.assertEqual(self.user1.profile.friends.all().count(), 2)
        self.assertEqual(self.user1.profile.friends.all()[0].user.pk, self.user2.pk)
        self.assertEqual(self.user1.profile.friends.all()[1].user.pk, self.user3.pk)
        self.assertEqual(self.user2.profile.friends.all().count(), 1)
        self.assertEqual(self.user2.profile.friends.all()[0].user.pk, self.user1.pk)
        self.assertEqual(self.user3.profile.friends.all().count(), 1)
        self.assertEqual(self.user3.profile.friends.all()[0].user.pk, self.user1.pk)

        response = self.client.get(reverse('friends.accept', args=[FR1.pk]))
        self.assertEqual(response.status_code, 404)

        # Only the 'to' can accept it
        FR3 = FriendRequest(user=self.user3, to=self.user2)
        FR3.save()
        response = self.client.get(reverse('friends.accept', args=[FR3.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cancel(self):
        FR1 = FriendRequest(user=self.user1, to=self.user3)
        FR1.save()
        FR2 = FriendRequest(user=self.user2, to=self.user1)
        FR2.save()
        self.assertEqual(FriendRequest.objects.all().count(), 2)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.cancel', args=[FR1.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.assertEqual(FriendRequest.objects.all()[0].pk, FR2.pk)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.cancel', args=[FR1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_refuse(self):
        FR1 = FriendRequest(user=self.user1, to=self.user3)
        FR1.save()
        FR2 = FriendRequest(user=self.user2, to=self.user1)
        FR2.save()
        self.assertEqual(FriendRequest.objects.all().count(), 2)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.refuse', args=[FR2.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.refuse', args=[FR1.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

    def test_delete(self):
        self.user1.profile.friends.add(self.user2.profile)
        self.assertEqual(self.user1.profile.friends.all().count(), 1)
        self.assertEqual(self.user2.profile.friends.all().count(), 1)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.delete', args=[self.user2.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        # No error when the user to remove from the friend list is not a friend
        response = self.client.get(reverse('friends.delete', args=[self.user3.pk]))
        self.assertRedirects(response, reverse('accounts.profile'))


class OutingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alpha',
                                              'alpha@example.com',
                                              '12789azertyuiop')
        self.user1.first_name = 'Alpha'
        self.user1.last_name = 'Tester'
        self.user1.save()
        self.user1.profile = Profile.objects.create(user=self.user1)
        self.client.login(username='alpha', password='12789azertyuiop')

        self.user2 = User.objects.create_user('Beta',
                                              'beta@example.org',
                                              'ertyfjnbfvfceqsryuj')
        self.user2.first_name = 'Beta'
        self.user2.last_name = 'Testing'
        self.user2.save()
        self.user2.profile = Profile.objects.create(user=self.user2)

        self.user3 = User.objects.create_user('Gamma',
                                              'gamma@example.net',
                                              'gzgvaryurvyyjchrvyhubtr')
        self.user3.first_name = 'Gamma'
        self.user3.last_name = 'Ray'
        self.user3.save()
        self.user3.profile = Profile.objects.create(user=self.user3)

        # user1 and user2 are friends
        self.user1.profile.friends.add(self.user2.profile)

        current_time = datetime.utcnow().replace(tzinfo=utc)
        # 3 outings for user1, and one for each user 2 and user3
        self.outing1 = Outing.objects.create(user=self.user1, beginning=current_time,
                                             ending=current_time, alert=current_time,
                                             latitude=1, longitude=1, status=CONFIRMED)
        self.outing2 = Outing.objects.create(user=self.user1, beginning=current_time,
                                             ending=current_time, alert=current_time,
                                             latitude=1, longitude=1, status=DRAFT)
        self.outing3 = Outing.objects.create(user=self.user1, beginning=current_time,
                                             ending=current_time, alert=current_time,
                                             latitude=1, longitude=1, status=FINISHED)
        self.outing4 = Outing.objects.create(user=self.user2, beginning=current_time,
                                             ending=current_time, alert=current_time,
                                             latitude=1, longitude=1, status=FINISHED)
        self.outing5 = Outing.objects.create(user=self.user3, beginning=current_time,
                                             ending=current_time, alert=current_time,
                                             latitude=1, longitude=1, status=CONFIRMED)

    def test_index(self):
        response = self.client.get(reverse('outings.index'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context

        self.assertEqual(len(ctx['user_outings_confirmed']), 1)
        self.assertEqual(ctx['user_outings_confirmed'][0], self.outing1)
        self.assertEqual(len(ctx['user_outings_draft']), 1)
        self.assertEqual(ctx['user_outings_draft'][0], self.outing2)
        self.assertEqual(len(ctx['user_outings_finished']), 1)
        self.assertEqual(ctx['user_outings_finished'][0], self.outing3)
        self.assertEqual(len(ctx['friends_outings_confirmed']), 0)
        self.assertEqual(len(ctx['friends_outings_draft']), 0)
        self.assertEqual(len(ctx['friends_outings_finished']), 1)
        self.assertEqual(ctx['friends_outings_finished'][0], self.outing4)

    def test_details(self):
        response = self.client.get(reverse('outings.details', args=[self.outing1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['outing'], self.outing1)
        response = self.client.get(reverse('outings.details', args=[self.outing2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['outing'], self.outing2)
        response = self.client.get(reverse('outings.details', args=[self.outing3.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['outing'], self.outing3)
        response = self.client.get(reverse('outings.details', args=[self.outing4.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['outing'], self.outing4)
        response = self.client.get(reverse('outings.details', args=[self.outing5.pk]))
        self.assertEqual(response.status_code, 404)
