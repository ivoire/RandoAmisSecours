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

from django.contrib import admin
from django.utils.timezone import datetime, utc
from RandoAmisSecours.models import *


class OutingAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'beginning', 'ending', 'alert', 'finished', 'not_running', 'not_late', 'not_alerting')
    ordering = ('-beginning', '-ending', '-alert', 'name')

    def finished(self, outing):
        return outing.status == FINISHED

    def not_running(self, outing):
        now = datetime.utcnow().replace(tzinfo=utc)
        return not outing.beginning <= now

    def not_late(self, outing):
        now = datetime.utcnow().replace(tzinfo=utc)
        return not outing.ending <= now

    def not_alerting(self, outing):
        now = datetime.utcnow().replace(tzinfo=utc)
        return not outing.alert <= now

    finished.boolean = True
    not_running.boolean = True
    not_late.boolean = True
    not_alerting.boolean = True


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'language', 'timezone')


class GPSPointAdmin(admin.ModelAdmin):
    list_display = ('outing', 'date', 'latitude', 'longitude', 'precision')
    ordering = ('outing', 'date')


admin.site.register(FriendRequest)
admin.site.register(Outing, OutingAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(GPSPoint, GPSPointAdmin)
