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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import datetime, utc

from tastypie.test import ResourceTestCase

from RandoAmisSecours.models import FriendRequest, Outing, Profile
from RandoAmisSecours.models import CONFIRMED, DRAFT, FINISHED


class TemplatesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('azertyuiop',
                                             'django.test@project.org',
                                             '12789azertyuiop')
        self.user.profile = Profile.objects.create(user=self.user)
        self.client.login(username='azertyuiop', password='12789azertyuiop')

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
        self.helper_template(reverse('password_reset_complete'), 'account/password_reset_complete.html')
        self.helper_template(reverse('accounts.logout'), 'account/logged_out.html')
        self.helper_template(reverse('accounts.login'), 'account/login.html')

    def test_profile(self):
        self.helper_template(reverse('accounts.register'), 'account/register.html')
        self.helper_template(reverse('accounts.register.confirm', args=[self.user.pk, self.user.profile.hash_id]), 'account/confirm.html')
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
        self.user.profile = Profile.objects.create(user=self.user, timezone='Europe/Paris', language='fr')
        self.user2 = User.objects.create_user('zarterzh',
                                              'gzeryztye@example.org',
                                              'help')
        self.user2.profile = Profile.objects.create(user=self.user2, timezone='Europe/London', language='en')

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
        self.assertFalse(ctx['error'])

        # An empty query
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), ''))
        ctx = response.context
        self.assertEqual(ctx['query'], '')
        self.assertEqual(ctx['results'], None)
        self.assertFalse(ctx['error'])

        # Match on queries
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'sop'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'sop')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user3.profile)
        self.assertFalse(ctx['error'])

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'Sopho'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'Sopho')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user3.profile)
        self.assertFalse(ctx['error'])

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'S'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'S')
        self.assertEqual(ctx['results'], None)
        self.assertTrue(ctx['error'])

        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'alpha'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'alpha')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user2.profile)
        self.assertFalse(ctx['error'])

        # Does not match the requester
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'ras'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'ras')
        self.assertEqual(len(ctx['results']), 0)
        self.assertFalse(ctx['error'])

        # match the emails
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'project.org'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'project.org')
        self.assertEqual(len(ctx['results']), 0)
        self.assertFalse(ctx['error'])

        # Change the logged-in user
        self.client.login(username='tester', password='ertyfjnbfvfceqsryuj')
        response = self.client.get("%s?query=%s" % (reverse('friends.search'), 'Sec'))
        ctx = response.context
        self.assertEqual(ctx['query'], 'Sec')
        self.assertEqual(len(ctx['results']), 1)
        self.assertEqual(ctx['results'][0], self.user1.profile)
        self.assertFalse(ctx['error'])

    def test_invite(self):
        response = self.client.get(reverse('friends.invite', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('friends.invite', args=[self.user2.pk]))
        self.assertRedirects(response, reverse('friends.search'))
        self.assertEqual(FriendRequest.objects.all().count(), 1)
        self.helper_compare_FR(FriendRequest.objects.all()[0], user=self.user1, to=self.user2)
        self.assertEqual(self.user1.profile.friends.all().count(), 0)
        self.assertEqual(self.user2.profile.friends.all().count(), 0)
        self.assertEqual(self.user3.profile.friends.all().count(), 0)

        response = self.client.get(reverse('friends.invite', args=[self.user3.pk]))
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
        self.user1.profile = Profile.objects.create(user=self.user1, timezone='Europe/Paris', language='fr')
        self.client.login(username='alpha', password='12789azertyuiop')

        self.user2 = User.objects.create_user('Beta',
                                              'beta@example.org',
                                              'ertyfjnbfvfceqsryuj')
        self.user2.first_name = 'Beta'
        self.user2.last_name = 'Testing'
        self.user2.save()
        self.user2.profile = Profile.objects.create(user=self.user2, timezone='Europe/London', language='en')

        self.user3 = User.objects.create_user('Gamma',
                                              'gamma@example.net',
                                              'gzgvaryurvyyjchrvyhubtr')
        self.user3.first_name = 'Gamma'
        self.user3.last_name = 'Ray'
        self.user3.save()
        self.user3.profile = Profile.objects.create(user=self.user3, timezone='America/Chicago', language='en')

        # user1 and user2 are friends
        self.user1.profile.friends.add(self.user2.profile)

        date = datetime(2011, 2, 15, 2, 0).replace(tzinfo=utc)
        # 3 outings for user1, and one for each user 2 and user3
        self.outing1 = Outing.objects.create(user=self.user1, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1, longitude=1, status=CONFIRMED)
        date = datetime(2011, 2, 15, 2, 10).replace(tzinfo=utc)
        self.outing2 = Outing.objects.create(user=self.user1, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1, longitude=1, status=DRAFT)
        date = datetime(2012, 11, 1, 6, 30).replace(tzinfo=utc)
        self.outing3 = Outing.objects.create(user=self.user1, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1, longitude=1, status=FINISHED)
        date = datetime(2013, 4, 10, 22, 0).replace(tzinfo=utc)
        self.outing4 = Outing.objects.create(user=self.user2, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1, longitude=1, status=FINISHED)
        date = datetime(2014, 2, 1, 8, 0).replace(tzinfo=utc)
        self.outing5 = Outing.objects.create(user=self.user3, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1, longitude=1, status=DRAFT)

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

    def test_confirm(self):
        # Initial state
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

        # Confirm one outing
        response = self.client.get(reverse('outings.confirm', args=[self.outing2.pk]))
        self.assertRedirects(response, reverse('outings.index'))

        # Test it
        response = self.client.get(reverse('outings.index'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['user_outings_confirmed']), 2)
        self.assertEqual(ctx['user_outings_confirmed'][0], self.outing1)
        self.assertEqual(ctx['user_outings_confirmed'][1], self.outing2)
        self.assertEqual(len(ctx['user_outings_draft']), 0)
        self.assertEqual(len(ctx['user_outings_finished']), 1)
        self.assertEqual(ctx['user_outings_finished'][0], self.outing3)
        self.assertEqual(len(ctx['friends_outings_confirmed']), 0)
        self.assertEqual(len(ctx['friends_outings_draft']), 0)
        self.assertEqual(len(ctx['friends_outings_finished']), 1)
        self.assertEqual(ctx['friends_outings_finished'][0], self.outing4)

        # Cannot confirm others outings
        response = self.client.get(reverse('outings.confirm', args=[self.outing5.pk]))
        self.assertRedirects(response, reverse('outings.index'))
        self.assertEqual(Outing.objects.get(pk=self.outing5.pk).status, DRAFT)

    def test_finish(self):
        # Initial state
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

        # Confirm one outing
        response = self.client.get(reverse('outings.finish', args=[self.outing1.pk]))
        self.assertRedirects(response, reverse('outings.index'))

        # Test it
        response = self.client.get(reverse('outings.index'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['user_outings_confirmed']), 0)
        self.assertEqual(len(ctx['user_outings_draft']), 1)
        self.assertEqual(ctx['user_outings_draft'][0], self.outing2)
        self.assertEqual(len(ctx['user_outings_finished']), 2)
        self.assertEqual(ctx['user_outings_finished'][0], self.outing1)
        self.assertEqual(ctx['user_outings_finished'][1], self.outing3)
        self.assertEqual(len(ctx['friends_outings_confirmed']), 0)
        self.assertEqual(len(ctx['friends_outings_draft']), 0)
        self.assertEqual(len(ctx['friends_outings_finished']), 1)
        self.assertEqual(ctx['friends_outings_finished'][0], self.outing4)

        # Cannot finish others outings
        response = self.client.get(reverse('outings.finish', args=[self.outing5.pk]))
        self.assertRedirects(response, reverse('outings.index'))
        self.assertEqual(Outing.objects.get(pk=self.outing5.pk).status, DRAFT)

    def test_delete(self):
        # Initial state
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

        # Confirm one outing
        response = self.client.get(reverse('outings.delete', args=[self.outing1.pk]))
        self.assertRedirects(response, reverse('outings.index'))

        # Test it
        response = self.client.get(reverse('outings.index'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['user_outings_confirmed']), 0)
        self.assertEqual(len(ctx['user_outings_draft']), 1)
        self.assertEqual(ctx['user_outings_draft'][0], self.outing2)
        self.assertEqual(len(ctx['user_outings_finished']), 1)
        self.assertEqual(ctx['user_outings_finished'][0], self.outing3)
        self.assertEqual(len(ctx['friends_outings_confirmed']), 0)
        self.assertEqual(len(ctx['friends_outings_draft']), 0)
        self.assertEqual(len(ctx['friends_outings_finished']), 1)
        self.assertEqual(ctx['friends_outings_finished'][0], self.outing4)

        # delete more
        response = self.client.get(reverse('outings.delete', args=[self.outing2.pk]))
        self.assertRedirects(response, reverse('outings.index'))
        response = self.client.get(reverse('outings.delete', args=[self.outing3.pk]))
        self.assertRedirects(response, reverse('outings.index'))

        # Test it
        response = self.client.get(reverse('outings.index'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['user_outings_confirmed']), 0)
        self.assertEqual(len(ctx['user_outings_draft']), 0)
        self.assertEqual(len(ctx['user_outings_finished']), 0)
        self.assertEqual(len(ctx['friends_outings_confirmed']), 0)
        self.assertEqual(len(ctx['friends_outings_draft']), 0)
        self.assertEqual(len(ctx['friends_outings_finished']), 1)
        self.assertEqual(ctx['friends_outings_finished'][0], self.outing4)

        # cannot delete others outings
        response = self.client.get(reverse('outings.delete', args=[self.outing5.pk]))
        self.assertRedirects(response, reverse('outings.index'))
        self.assertEqual(Outing.objects.get(pk=self.outing5.pk).status, DRAFT)

    def test_create(self):
        # Initial state
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

        # Test errors
        response = self.client.post(reverse('outings.create'), {})
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertNotEqual(ctx['form']['name'].errors, None)
        self.assertNotEqual(ctx['form']['description'].errors, None)
        self.assertNotEqual(ctx['form']['beginning'].errors, None)
        self.assertNotEqual(ctx['form']['ending'].errors, None)
        self.assertNotEqual(ctx['form']['alert'].errors, None)
        self.assertNotEqual(ctx['form']['latitude'].errors, None)
        self.assertNotEqual(ctx['form']['longitude'].errors, None)

        data = {'name': 'Les Drus',
                'description': 'Les fameux Drus',
                'beginning': datetime(2013, 10, 11, 14, 0),
                'ending': datetime(2013, 10, 11, 4, 0),
                'alert': datetime(2013, 10, 11, 2, 0),
                'latitude': 45.93194945945032,
                'longitude': 6.956169605255127}
        response = self.client.post(reverse('outings.create'), data)
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx['form']['name'].errors, [])
        self.assertEqual(ctx['form']['description'].errors, [])
        self.assertNotEqual(ctx['form']['beginning'].errors, [])
        self.assertNotEqual(ctx['form']['ending'].errors, None)
        self.assertNotEqual(ctx['form']['alert'].errors, None)
        self.assertEqual(ctx['form']['latitude'].errors, [])
        self.assertEqual(ctx['form']['longitude'].errors, [])

        # Create a good sample
        data = {'name': 'Les Drus',
                'description': 'Les fameux Drus',
                'beginning': datetime(2013, 10, 11, 4, 0),
                'ending': datetime(2013, 10, 11, 14, 0),
                'alert': datetime(2013, 10, 11, 18, 0),
                'latitude': 45.93194945945032,
                'longitude': 6.956169605255127}
        response = self.client.post(reverse('outings.create'), data)
        outing = Outing.objects.get(name='Les Drus')
        self.assertRedirects(response, reverse('outings.details', args=[outing.pk]))

        self.assertEqual(outing.beginning, datetime(2013, 10, 11, 2, 0).replace(tzinfo=utc))
        self.assertEqual(outing.ending, datetime(2013, 10, 11, 12, 0).replace(tzinfo=utc))
        self.assertEqual(outing.alert, datetime(2013, 10, 11, 16, 0).replace(tzinfo=utc))

        # Create the same sample from another user
        # Create a good sample
        self.client.logout()
        self.client.login(username='Beta', password='ertyfjnbfvfceqsryuj')
        data = {'name': 'Les Drus',
                'description': 'Les fameux Drus une seconde fois',
                'beginning': datetime(2013, 10, 11, 4, 0),
                'ending': datetime(2013, 10, 11, 14, 0),
                'alert': datetime(2013, 10, 11, 18, 0),
                'latitude': 45.93194945945032,
                'longitude': 6.956169605255127}
        response = self.client.post(reverse('outings.create'), data)
        outing = Outing.objects.get(name='Les Drus', user=self.user2)
        self.assertRedirects(response, reverse('outings.details', args=[outing.pk]))

        self.assertEqual(outing.beginning, datetime(2013, 10, 11, 3, 0).replace(tzinfo=utc))
        self.assertEqual(outing.ending, datetime(2013, 10, 11, 13, 0).replace(tzinfo=utc))
        self.assertEqual(outing.alert, datetime(2013, 10, 11, 17, 0).replace(tzinfo=utc))

    def test_update(self):
        # Test the errors
        response = self.client.post(reverse('outings.update', args=[self.outing5.pk]))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('outings.update', args=[self.outing3.pk]))
        self.assertEqual(response.status_code, 404)


class AccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alpha',
                                              'alpha@example.com',
                                              '12789azertyuiop')
        self.user1.first_name = 'Alpha'
        self.user1.last_name = 'Tester'
        self.user1.save()
        self.user1.profile = Profile.objects.create(user=self.user1, timezone='Europe/Paris', language='fr')
        self.client.login(username='alpha', password='12789azertyuiop')

    def test_profile(self):
        response = self.client.get(reverse('accounts.profile'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx['user'], self.user1)
        self.assertEqual(len(ctx['friend_requests']), 0)
        self.assertEqual(len(ctx['friend_requests_sent']), 0)
        self.assertEqual(response.client.session['django_language'], 'fr')
        self.assertEqual(response.client.session['django_timezone'], 'Europe/Paris')

        # Update the profile and try again
        data = {'first_name': 'new one',
                'last_name': 'another one',
                'phone_number': '0123456789',
                'language': 'en',
                'timezone': 'Europe/London'
                }
        response = self.client.post(reverse('accounts.profile.update'), data)
        self.assertRedirects(response, reverse('accounts.profile'))

        response = self.client.get(reverse('accounts.profile'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['friend_requests']), 0)
        self.assertEqual(len(ctx['friend_requests_sent']), 0)
        self.assertEqual(ctx['user'].first_name, 'new one')
        self.assertEqual(ctx['user'].last_name, 'another one')
        self.assertEqual(ctx['user'].profile.phone_number, '0123456789')
        self.assertEqual(ctx['user'].profile.language, 'en')
        self.assertEqual(ctx['user'].profile.timezone, 'Europe/London')
        self.assertEqual(response.client.session['django_language'], 'en')
        self.assertEqual(response.client.session['django_timezone'], 'Europe/London')

        # Try some errors now
        # Not setting the last_name is not an error
        data = {'first_name': 'new one',
                'last_name': '',
                'phone_number': '0123456789',
                'language': 'fr',
                'timezone': 'Europe/London'
                }
        response = self.client.post(reverse('accounts.profile.update'), data)
        self.assertRedirects(response, reverse('accounts.profile'))

        response = self.client.get(reverse('accounts.profile'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['friend_requests']), 0)
        self.assertEqual(len(ctx['friend_requests_sent']), 0)
        self.assertEqual(ctx['user'].first_name, 'new one')
        self.assertEqual(ctx['user'].last_name, '')
        self.assertEqual(ctx['user'].profile.phone_number, '0123456789')
        self.assertEqual(ctx['user'].profile.language, 'fr')
        self.assertEqual(ctx['user'].profile.timezone, 'Europe/London')
        self.assertEqual(response.client.session['django_language'], 'fr')
        self.assertEqual(response.client.session['django_timezone'], 'Europe/London')

        # Not setting some fields
        data = {}
        response = self.client.post(reverse('accounts.profile.update'), data)
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertNotEqual(ctx['user_form']['first_name'].errors, None)
        self.assertEqual(ctx['user_form']['last_name'].errors, [])
        self.assertNotEqual(ctx['profile_form']['phone_number'].errors, None)
        self.assertNotEqual(ctx['profile_form']['language'].errors, None)
        self.assertNotEqual(ctx['profile_form']['timezone'].errors, None)
        self.assertEqual(response.client.session['django_language'], 'fr')
        self.assertEqual(response.client.session['django_timezone'], 'Europe/London')

    def test_friend_request(self):
        self.user2 = User.objects.create_user('tester',
                                              'tester@project.org',
                                              'ertyfjnbfvfceqsryuj')
        self.user3 = User.objects.create_user('Sophocle',
                                              'sophocle@project.org',
                                              'gzgvaryurvyyjchrvyhubtr')
        FR = FriendRequest(user=self.user1, to=self.user2)
        FR.save()
        FR2 = FriendRequest(user=self.user3, to=self.user1)
        FR2.save()
        FR3 = FriendRequest(user=self.user3, to=self.user2)
        FR3.save()

        response = self.client.get(reverse('accounts.profile'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(len(ctx['friend_requests']), 1)
        self.assertEqual(ctx['friend_requests'][0].user, self.user3)
        self.assertEqual(ctx['friend_requests'][0].to, self.user1)
        self.assertEqual(len(ctx['friend_requests_sent']), 1)
        self.assertEqual(ctx['friend_requests_sent'][0].user, self.user1)
        self.assertEqual(ctx['friend_requests_sent'][0].to, self.user2)


class APITest(ResourceTestCase):
    def setUp(self):
        super(APITest, self).setUp()

        self.user1 = User.objects.create_user('ras', 'ras@example.com', 'mdp')
        self.user1.first_name = 'Rando'
        self.user1.last_name = 'Amis'
        self.user1.save()
        self.user1.profile = Profile.objects.create(user=self.user1, timezone='Europe/Paris', language='fr')
        self.client.login(username='ras', password='mdp')

        self.user2 = User.objects.create_user('ras_friend', 'ras_friend@example.com', 'mdp2')
        self.user2.first_name = 'Rando_friend'
        self.user2.last_name = 'Amis'
        self.user2.save()
        self.user2.profile = Profile.objects.create(user=self.user2, timezone='Europe/London', language='en')
        self.user2.profile.friends.add(self.user1.profile)

        self.user3 = User.objects.create_user('friend_of_friend', 'friend_of_friend@example.com', 'mdp3')
        self.user3.first_name = 'Friend'
        self.user3.last_name = 'another_one'
        self.user3.save()
        self.user3.profile = Profile.objects.create(user=self.user3, timezone='Europe/Paris', language='fr')
        self.user3.profile.friends.add(self.user2.profile)

        date = datetime(2011, 2, 15, 2, 0).replace(tzinfo=utc)
        self.outing1 = Outing.objects.create(user=self.user1, beginning=date,
                                             ending=date, alert=date,
                                             latitude=1.23, longitude=3.21, status=CONFIRMED)
        date = datetime(2011, 2, 15, 2, 10).replace(tzinfo=utc)
        self.outing2 = Outing.objects.create(user=self.user2, beginning=date,
                                             ending=date, alert=date,
                                             latitude=2.42, longitude=4.567890123, status=CONFIRMED)
        date = datetime(2011, 2, 15, 2, 10).replace(tzinfo=utc)
        self.outing3 = Outing.objects.create(user=self.user2, beginning=date,
                                             ending=date, alert=date,
                                             latitude=2.45678, longitude=0.98765432, status=CONFIRMED)
        date = datetime(2011, 2, 15, 2, 10).replace(tzinfo=utc)
        self.outing4 = Outing.objects.create(user=self.user3, beginning=date,
                                             ending=date, alert=date,
                                             latitude=4.12673661, longitude=0.65231, status=CONFIRMED)

    def get_credentials(self):
        return self.create_basic(username='ras', password='mdp')

    def test_user_list(self):
        # List the users
        resp = self.api_client.get('/api/1.0/user/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'email': self.user1.email,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name,
            'profile': "/api/1.0/profile/%d/" % (self.user1.profile.pk),
            'resource_uri': "/api/1.0/user/%d/" % (self.user1.pk)
        })
        self.assertEqual(self.deserialize(resp)['objects'][1], {
            'email': self.user2.email,
            'first_name': self.user2.first_name,
            'last_name': self.user2.last_name,
            'profile': "/api/1.0/profile/%d/" % (self.user2.profile.pk),
            'resource_uri': "/api/1.0/user/%d/" % (self.user2.pk)
        })

        # Try with user2
        self.client.login(username='ras_friend', password='mdp2')
        resp = self.api_client.get('/api/1.0/user/', format='json', authentication=self.create_basic(username='ras_friend', password='mdp2'))
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 3)
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'email': self.user1.email,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name,
            'profile': "/api/1.0/profile/%d/" % (self.user1.profile.pk),
            'resource_uri': "/api/1.0/user/%d/" % (self.user1.pk)
        })
        self.assertEqual(self.deserialize(resp)['objects'][1], {
            'email': self.user2.email,
            'first_name': self.user2.first_name,
            'last_name': self.user2.last_name,
            'profile': "/api/1.0/profile/%d/" % (self.user2.profile.pk),
            'resource_uri': "/api/1.0/user/%d/" % (self.user2.pk)
        })
        self.assertEqual(self.deserialize(resp)['objects'][2], {
            'email': self.user3.email,
            'first_name': self.user3.first_name,
            'last_name': self.user3.last_name,
            'profile': "/api/1.0/profile/%d/" % (self.user3.profile.pk),
            'resource_uri': "/api/1.0/user/%d/" % (self.user3.pk)
        })

    def test_user_modification(self):
        """ This is not allowed for the moment """
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/1.0/user/', format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/1.0/user/', format='json', authentication=self.get_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.put("/api/1.0/user/%d/" % (self.user1.pk), format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.put("/api/1.0/user/%d/" % (self.user1.pk), format='json', authentication=self.get_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.delete("/api/1.0/user/%d/" % (self.user1.pk), format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.delete("/api/1.0/user/%d/" % (self.user1.pk), format='json', authentication=self.get_credentials()))

    def test_profile_list(self):
        # List the profiles
        resp = self.api_client.get('/api/1.0/profile/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'friends': ["/api/1.0/profile/%d/" % (self.user2.pk)],
            'timezone': self.user1.profile.timezone,
            'language': self.user1.profile.language,
            'phone_number': self.user1.profile.phone_number,
            'user': "/api/1.0/user/%d/" % (self.user1.pk),
            'resource_uri': "/api/1.0/profile/%d/" % (self.user1.profile.pk)
        })
        self.assertEqual(self.deserialize(resp)['objects'][1], {
            'phone_number': self.user2.profile.phone_number,
            'user': "/api/1.0/user/%d/" % (self.user2.pk),
            'resource_uri': "/api/1.0/profile/%d/" % (self.user2.profile.pk)

        })

        # Try with user2
        self.client.login(username='ras_friend', password='mdp2')
        resp = self.api_client.get('/api/1.0/profile/', format='json', authentication=self.create_basic(username='ras_friend', password='mdp2'))
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 3)

    def test_profile_modification(self):
        """ This is not allowed for the moment """
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/1.0/profile/', format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/1.0/profile/', format='json', authentication=self.get_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.put("/api/1.0/profile/%d/" % (self.user1.profile.pk), format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.put("/api/1.0/profile/%d/" % (self.user1.profile.pk), format='json', authentication=self.get_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.delete("/api/1.0/profile/%d/" % (self.user1.profile.pk), format='json', data=''))
        self.assertHttpMethodNotAllowed(self.api_client.delete("/api/1.0/profile/%d/" % (self.user1.profile.pk), format='json', authentication=self.get_credentials()))

    def test_outing_list(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/1.0/outing/', format='json'))
        resp = self.api_client.get('/api/1.0/outing/', format='json', authentication=self.get_credentials())
        self.assertEqual(len(self.deserialize(resp)['objects']), 3)
