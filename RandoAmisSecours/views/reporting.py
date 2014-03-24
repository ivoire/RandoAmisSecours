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

from __future__ import unicode_literals

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils.timezone import datetime, utc

from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, FINISHED

from datetime import timedelta


@staff_member_required
def index(request):
    user_count = User.objects.count()
    return render_to_response('RandoAmisSecours/reporting/index.html',
                              {'user_count': user_count},
                              context_instance=RequestContext(request))

@staff_member_required
def outings(request):
    return render_to_response('RandoAmisSecours/reporting/outings.html',
                              context_instance=RequestContext(request))

@staff_member_required
def users(request):
    now = datetime.utcnow().replace(tzinfo=utc)
    users_list = User.objects.all()

    joining_dates = [0] * 366
    last_logins = [0] * 366
    for user in users_list:
        days_delta = (now - user.date_joined).days
        if days_delta <= 365:
            joining_dates[365 - days_delta] += 1

        days_delta = (now - user.last_login).days
        if days_delta <= 365:
            last_logins[365 - days_delta] += 1

    return render_to_response('RandoAmisSecours/reporting/users.html',
                              {'joining_dates': joining_dates,
                               'last_logins': last_logins},
                              context_instance=RequestContext(request))
