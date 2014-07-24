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

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.utils import timezone, translation

import logging
import json
import pytz
from SMSForward import providers

logger = logging.getLogger('ras.utils')


class Localize(object):
    def __init__(self, language, timezone):
        self.language = language
        self.timezone = timezone

    def __enter__(self):
        if self.language:
            translation.activate(self.language)
        if self.timezone:
            timezone.activate(pytz.timezone(self.timezone))

    def __exit__(self, type_name, value, traceback):
        if self.timezone:
            timezone.deactivate()
        if self.language:
            translation.deactivate()


def send_localized_mail(user, subject, template_name, ctx):
    with Localize(user.profile.language,
                  user.profile.timezone):
        send_mail_help(user, subject, template_name, ctx)


def send_mail_help(user, subject, template_name, ctx):
    body = loader.render_to_string(template_name, ctx)
    logger.info("Sending email to '%s' ('%s')", user.get_full_name(),
                user.email, extra={'data': ctx})
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_sms(user, template_name, ctx):
    # Check that the provider is available
    if not user.profile.provider or not user.profile.provider_data:
        return

    logger.info("Sending SMS to '%s' ('%s')",
                user.get_full_name(), user.profile.provider,
                extra={'data': ctx})
    msg = loader.render_to_string(template_name, ctx)

    # Create the provider object
    try:
        provider = providers.create(user.profile.provider,
                                    json.loads(user.profile.provider_data))
    except NotImplementedError:
        logger.error("Unknown provider '%s'", user.profile.provider,
                     exc_info=True,
                     extra={'data': {'user': user.get_full_name(),
                                     'provider': user.profile.provider}})

    try:
        provider.send_message(msg)
        raise Exception
    except Exception:
        logger.error("Unable to send SMS", exc_info=True,
                     extra={'data': {'user': user.get_full_name(),
                                     'provider': user.profile.provider}})
