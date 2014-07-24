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

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.timesince import timesince
from django.utils.timezone import datetime, utc
from django.utils.translation import ugettext_lazy as _

from RandoAmisSecours.models import Outing, CONFIRMED, DRAFT
from RandoAmisSecours.utils import Localize, send_mail_help, send_sms

import logging
from optparse import make_option

logger = logging.getLogger('ras.alert')


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
                    help='Alerting interval'),
        make_option('--url',
                    dest='base_url',
                    help='Base URL of the website'))

    def handle(self, *args, **kwargs):
        if kwargs.get('base_url', None) is None:
            raise CommandError('url option is required')

        logger.info("Running Alert script")
        now = datetime.utcnow().replace(tzinfo=utc)

        # Transform all DRAFT into CONFIRMED if the beginning is over
        logger.debug('Transforming DRAFTs')
        outings = Outing.objects.filter(status=DRAFT, beginning__lt=now)
        for outing in outings:
            logger.info("Confirm: '%s' (owner: '%s')", outing.name,
                        outing.user.get_full_name())
            outing.status = CONFIRMED
            outing.save()

        # Grab all late outings
        logger.debug('Alerting owner and friends')
        outings = Outing.objects.filter(status=CONFIRMED, ending__lt=now)

        for outing in outings:
            logger.debug("Inspecting: '%s' (owner: '%s')", outing.name,
                         outing.user.get_full_name())
            # Late outings
            if outing.ending <= now and now < outing.alert:
                logger.debug(' |-> Late')
                minutes = (now - outing.ending).seconds / 60.0
                minutes = minutes % kwargs['alert']

                if 0 <= minutes and minutes < kwargs['interval']:
                    logger.debug(' |--> Alerting the owner')
                    logger.debug("     |-> %s", outing.user.get_full_name())
                    logger.debug("     |--> email: %s", outing.user.email)
                    logger.debug("     |--> provider: %s", outing.user.profile.provider)
                    # send a mail to the user, translated into the right language
                    with Localize(outing.user.profile.language,
                                  outing.user.profile.timezone):
                        send_mail_help(outing.user, _('[R.A.S] Alert'),
                                       'RandoAmisSecours/alert/late.html',
                                       {'URL': "%s%s" % (kwargs['base_url'],
                                                         reverse('outings.details', args=[outing.pk])),
                                        'SAFE_URL': "%s%s" % (kwargs['base_url'],
                                                              reverse('outings.finish', args=[outing.pk]))})
                        send_sms(outing.user, 'RandoAmisSecours/alert/late.txt',
                                 {'name': outing.name})

            # Alerting outings
            elif outing.alert <= now:
                logger.debug(' |-> Alert')
                minutes = (now - outing.alert).seconds / 60.0
                minutes = minutes % kwargs['alert']

                if 0 <= minutes and minutes < kwargs['interval']:
                    logger.debug(' |--> Alerting now')
                    friend_count = outing.user.profile.friends.count()
                    logger.debug(" |---> %d friends to contact", friend_count)
                    # Send on mail per user translated into the right language
                    for friend_profile in outing.user.profile.friends.all():
                        logger.debug("      |-> %s", friend_profile.user.get_full_name())
                        logger.debug("      |--> email: %s", friend_profile.user.email)
                        logger.debug("      \--> provider: %s", friend_profile.provider)
                        with Localize(friend_profile.language,
                                      friend_profile.timezone):
                            send_mail_help(friend_profile.user, _('[R.A.S] Alert'),
                                           'RandoAmisSecours/alert/alert.html',
                                           {'fullname': outing.user.get_full_name(),
                                            'URL': "%s%s" % (kwargs['base_url'], reverse('outings.details', args=[outing.pk])),
                                            'name': outing.name,
                                            'ending': outing.ending})
                            send_sms(friend_profile.user,
                                     'RandoAmisSecours/alert/alert.txt',
                                     {'fullname': outing.user.get_full_name(),
                                      'name': outing.name,
                                      'ending': timesince(outing.ending)})
                    logger.debug(' |--> Alerting the owner')
                    logger.debug("     |-> %s", outing.user.get_full_name())
                    logger.debug("     |--> email: %s", outing.user.email)
                    logger.debug("     |--> provider: %s", outing.user.profile.provider)
                    with Localize(outing.user.profile.language,
                                  outing.user.profile.timezone):
                        send_mail_help(outing.user, _('[R.A.S] Alert'),
                                       'RandoAmisSecours/alert/alert_owner.html',
                                       {'fullname': outing.user.get_full_name(),
                                        'URL': "%s%s" % (kwargs['base_url'],
                                                         reverse('outings.details', args=[outing.pk])),
                                        'name': outing.name,
                                        'ending': outing.ending,
                                        'friend_count': friend_count})
                        send_sms(outing.user,
                                 'RandoAmisSecours/alert/alert_owner.txt',
                                 {'name': outing.name,
                                  'ending': timesince(outing.ending)})

        logger.info("End of Alert script")
