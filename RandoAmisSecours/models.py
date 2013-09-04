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


from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import datetime, utc

import binascii
import os


# Outing status
DRAFT = 0
CONFIRMED = 1
LATE = 3
FINISHED = 4
CANCELED = 5
OUTING_STATUS = (
    (DRAFT, 'draft'),
    (CONFIRMED, 'confirmed'),
    (LATE, 'late'),
    (FINISHED, 'finished'),
    (CANCELED, 'canceled')
)


def random_hash():
    """ Create a random string of size 15 """
    return binascii.b2a_hex(os.urandom(15))


class Profile(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'

    user = models.OneToOneField(User)
    friends = models.ManyToManyField('self', blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    hash_id = models.CharField(unique=True, max_length=30, default=random_hash)

    def __unicode__(self):
        return unicode(self.user)


class Outing(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'
        ordering = ['begining', 'ending', 'alert', 'name']

    user = models.ForeignKey(User)

    # Visible information
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.IntegerField(choices=OUTING_STATUS, default=DRAFT)

    # Time frame: (begin, end, alert)
    begining = models.DateTimeField()
    ending = models.DateTimeField()
    alert = models.DateTimeField()

    # Position on the map
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return u"%s: %s" % (self.user.get_full_name(), self.name)

    def getPercents(self):
        current_time = datetime.utcnow().replace(tzinfo=utc)
        # now < begin < end < alert
        if current_time < self.begining:
            return (0, 0, 0)
        # begin < end < alert < now
        elif self.alert < current_time:
            return (0, 0, 100)
        # begin < now < end < alert
        elif current_time < self.ending:
            return (((current_time - self.begining).total_seconds()) / float((self.alert - self.begining).total_seconds()) * 100, 0, 0)
        # begin < end < now < alert
        else:
            assert(current_time < self.alert)
            return (((self.ending - self.begining).total_seconds()) / float((self.alert - self.begining).total_seconds()) * 100,
                    ((current_time - self.ending).total_seconds()) / float((self.alert - self.begining).total_seconds()) * 100,
                    0)

    def is_running(self):
        """ Return True if begining <= now < end """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.begining <= now and now < self.ending

    def is_late(self):
        """ Return True if end <= now < alert """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.ending <= now and now < self.alert

    def is_alerting(self):
        """ Return True if alert <= now """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.alert <= now
