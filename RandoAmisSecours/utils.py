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
from django.utils import timezone, translation, timesince

import json
import pytz
import providers


def send_localized_mail(user, subject, template_name, ctx):
    if user.profile.language:
        translation.activate(user.profile.language)
    if user.profile.timezone:
        timezone.activate(pytz.timezone(user.profile.timezone))

    body = loader.render_to_string(template_name, ctx)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])

    if user.profile.timezone:
        timezone.deactivate()
    if user.profile.language:
        translation.deactivate()


def send_localized_sms(user, template_name, outing):
    # Check that the provider is available
    if not user.profile.provider or not user.profile.provider_data:
        return

    if user.profile.language:
        translation.activate(user.profile.language)
    if user.profile.timezone:
        timezone.activate(pytz.timezone(user.profile.timezone))

    ctx = {'fullname': outing.user.get_full_name(),
           'name': outing.name,
           'ending': timesince.timesince(outing.ending)}
    msg = loader.render_to_string(template_name, ctx)

    # Create the provider object
    provider = providers.create(user.profile.provider,
                                json.loads(user.profile.provider_data))
    provider.send_message(msg)

    if user.profile.timezone:
        timezone.deactivate()
    if user.profile.language:
        translation.deactivate()
