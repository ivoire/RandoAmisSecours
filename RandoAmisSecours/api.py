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

from django.db.models import Q
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource

from RandoAmisSecours.models import Outing


class UserAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(pk=bundle.request.user.pk) |
                                  Q(profile__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        return (bundle.obj.pk == bundle.request.user.pk or
                bundle.obj.profile in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def update_detail(seld, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def delete_list(self, object_list, bundle):
        raise Unathorized('Deletion impossible')

    def delete_detail(self, object_list, bundle):
        raise Unathorized('Deletion impossible')


class OutingAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(user=bundle.request.user) | Q(user__profile__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        return (bundle.obj.user == bundle.request.user or
                bundle.obj.user in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        # TODO: is the user auto assigned
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        return [obj for obj in object_list if obj.user == bundle.request.user]

    def update_detail(seld, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        return [obj for obj in object_list if obj.user == bundle.request.user]

    def delete_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['first_name', 'last_name', 'email']
        allowed_method = ['get']
        authorization = UserAuthorization()


class OutingResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Outing.objects.all()
        resource_name = 'outing'
        fields = ['name', 'description', 'status', 'beginning', 'ending', 'alert', 'latitude', 'longitude']
        authorization = OutingAuthorization()
