# -*- coding: utf-8 -*-
# vim: set ts=4

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.timezone import datetime, utc
from django.utils.translation import ugettext_lazy as _

from RandoAmisSecours.models import Outing, Profile, CONFIRMED

from optparse import make_option


class Command(BaseCommand):
  args = None
  help = 'Alert the user or his friends that he is late'
  option_list = BaseCommand.option_list + (
    make_option('--interval',
                dest='interval',
                default=10,
                type=int,
                help='Check interval in minutes'),
    make_option('--alert',
                dest='alert',
                default=60,
                type=int,
                help='Alerting interval'))

  def handle(self, *args, **kwargs):
    self.stdout.write("Listing alerting outings")
    self.stdout.write("Interval %d" % (kwargs['interval']))

    now = datetime.utcnow().replace(tzinfo=utc)
    outings = Outing.objects.filter(status=CONFIRMED, alert__lt=now)

    for outing in outings:
      self.stdout.write(" - %s" % (outing.name))
      # Late outings
      if outing.ending <= now and now < outing.alert:
        minutes = (now - outing.alert).seconds / 60.0
        minutes = minutes % kwargs['alert']

        if 0 <= minutes and minutes < kwargs['interval']:
          self.stdout.write("Sending mail to owner")
          body = _("""
Hello,

you are late from you outing %(URL)s.

If you are back home safe, please click on %(SAFE_URL)s.

-- 
The R.A.S team""") % {'fullname': outing.user.get_full_name(),
                      'URL': reverse('outings.details', args=[outing.pk]),
                      'SAFE_URL': reverse('outings.finish', args=[outing.pk])}
          send_mail(_("[R.A.S] Alert"), body, settings.DEFAULT_FROM_EMAIL, outing.user.email)

      # Alerting outings
      elif outing.alert <= now:
        minutes = (now - outing.alert).seconds / 60.0
        minutes = minutes % kwargs['alert']

        self.stdout.write("  minutes: %d" % (minutes))
        if 0 <= minutes and minutes < kwargs['interval']:
          self.stdout.write("emailing friends")
          body = _("""
Hello,

%(fullname)s is late from his outing %(URL)s.

You can try to contact him to get more information about the situation.

-- 
The R.A.S team""") % {'fullname': outing.user.get_full_name(), 'URL': reverse('outings.details', args=[outing.pk])}
          emails = [f.user.email for f in outing.user.profile.friends.all()]
          send_mail(_("[R.A.S] Alert"), body, settings.DEFAULT_FROM_EMAIL, emails)
