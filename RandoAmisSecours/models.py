# -*- coding: utf-8 -*-
# vim: set ts=4

from django.contrib.auth.models import User
from django.db import models

import binascii
import os


# Outing status
DRAFT = 0
CONFIRMED = 1
LATE = 3
FINISHED = 3
CANCELED = 4
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

    user = models.ForeignKey(User)
    phone_number = models.CharField(max_length=30)
    hash_id = models.CharField(unique=True, max_length=30, default=random_hash)


class Outing(models.Model):
    class Meta:
        app_label = 'RandoAmisSecours'

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
