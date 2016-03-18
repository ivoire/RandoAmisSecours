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
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import datetime, utc
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext

from RandoAmisSecours.settings import LANGUAGES
import binascii
import json
import pytz
import os


# Outing status
DRAFT = 0
CONFIRMED = 1
LATE = 3
FINISHED = 4
CANCELED = 5
OUTING_STATUS = (
    (DRAFT, _('draft')),
    (CONFIRMED, _('confirmed')),
    (LATE, _('late')),
    (FINISHED, _('finished')),
    (CANCELED, _('canceled'))
)

PROVIDERS = (
    ('mobile.free.fr', 'Free Mobile France'),
)


def random_hash():
    """ Create a random string of size 30 """
    return binascii.b2a_hex(os.urandom(15))


@python_2_unicode_compatible
class Profile(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'

    user = models.OneToOneField(User)
    friends = models.ManyToManyField('self', blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    provider = models.CharField(max_length=30, blank=True, null=True, choices=PROVIDERS)
    provider_data = models.TextField(blank=True, null=True)
    hash_id = models.CharField(unique=True, max_length=30, default=random_hash)
    language = models.CharField(max_length=4, blank=True, null=True, choices=LANGUAGES)
    timezone = models.CharField(max_length=40, choices=[(tz, tz) for tz in pytz.all_timezones], default='UTC')

    def clean(self):
        if self.provider_data:
            try:
                json.loads(self.provider_data)
            except Exception:
                raise ValidationError({'provider_data': [ugettext('This should be JSON serialized')]})

        if self.timezone == 'UTC':
            raise ValidationError({'timezone': [ugettext('UTC is not valid timezone')]})

    def __str__(self):
        return "%s" % (self.user)


@python_2_unicode_compatible
class FriendRequest(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'

    user = models.ForeignKey(User, related_name='+')
    to = models.ForeignKey(User, related_name='+')
    creation = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s => %s" % (self.user.get_full_name(), self.to.get_full_name())


@python_2_unicode_compatible
class Outing(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'
        ordering = ['beginning', 'ending', 'alert', 'name']

    user = models.ForeignKey(User)

    # Visible information
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.IntegerField(choices=OUTING_STATUS, default=DRAFT)

    # Time frame: (begin, end, alert)
    beginning = models.DateTimeField()
    ending = models.DateTimeField()
    alert = models.DateTimeField()

    # Position on the map
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return "%s: %s" % (self.user.get_full_name(), self.name)

    def getPercents(self):
        current_time = datetime.utcnow().replace(tzinfo=utc)
        # now < begin < end < alert
        if current_time < self.beginning:
            return (0, 0, 0)
        # begin < end < alert < now
        elif self.alert < current_time:
            return (0, 0, 100)
        # begin < now < end < alert
        elif current_time < self.ending:
            return (((current_time - self.beginning).total_seconds()) / float((self.alert - self.beginning).total_seconds()) * 100, 0, 0)
        # begin < end < now < alert
        else:
            assert(current_time < self.alert)
            return (((self.ending - self.beginning).total_seconds()) / float((self.alert - self.beginning).total_seconds()) * 100,
                    ((current_time - self.ending).total_seconds()) / float((self.alert - self.beginning).total_seconds()) * 100,
                    0)

    def is_running(self):
        """ Return True if beginning <= now < end """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.beginning <= now and now < self.ending

    def is_late(self):
        """ Return True if end <= now < alert """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.ending <= now and now < self.alert

    def is_alerting(self):
        """ Return True if alert <= now """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.alert <= now

    is_running.boolean = True
    is_late.boolean = True
    is_alerting.boolean = True


@python_2_unicode_compatible
class GPSPoint(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'
        ordering = ['date']

    outing = models.ForeignKey(Outing)
    date = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    precision = models.IntegerField()

    def __str__(self):
        return "[%s] %s: (%f, %f)" % (self.outing.user.get_full_name(),
                                      self.outing.name, self.latitude,
                                      self.longitude)
