# -*- coding: utf-8 -*-
# vim: set ts=4

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import datetime, utc

from RandoAmisSecours.models import Outing, Profile, CONFIRMED


class Command(BaseCommand):
  args = None
  help = 'Alert the user or his friends that he is late'

  def handle(self, *args, **kwargs):
    self.stdout.write("Listing alerting outings")
    now = datetime.utcnow().replace(tzinfo=utc)
    outings = Outing.objects.filter(status=CONFIRMED, alert__lt=now)

    for outing in outings:
      self.stdout.write(" - %s" % (outing.name))
