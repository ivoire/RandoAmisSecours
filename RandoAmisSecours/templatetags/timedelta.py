# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2014 Rémi Duraffort
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

from django import template
from django.utils.timezone import datetime, utc
from django.utils.timesince import timesince
from django.utils.translation import ugettext as _
from datetime import datetime


register = template.Library()

@register.filter
def timedelta(value):
    if not value:
        return ''

    now = datetime.utcnow().replace(tzinfo=utc)
    if value > now:
        return _("in %s") % timesince(now, value)
    else:
        return timesince(value, now)
