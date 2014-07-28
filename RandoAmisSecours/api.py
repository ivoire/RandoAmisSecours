# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2013, 2014 Rémi Duraffort
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
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.models import ApiKey
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from RandoAmisSecours.models import Outing, Profile, GPSPoint


class UserAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(pk=bundle.request.user.pk) |
                                  Q(profile__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        # bundle.obj is a User
        return (bundle.obj.pk == bundle.request.user.pk or
                bundle.obj.profile in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def update_detail(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def delete_list(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')


class ProfileAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(user=bundle.request.user) |
                                  Q(pk__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        # bundle.obj is a Profile
        return (bundle.obj.user == bundle.request.user or
                bundle.obj in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def update_detail(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def delete_list(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')


class OutingAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(user=bundle.request.user) |
                                  Q(user__profile__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        # bundle.obj is an Outing
        return (bundle.obj.user == bundle.request.user or
                bundle.obj.user.profile in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def update_detail(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def delete_list(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')


class GPSPointAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(Q(outing__user__pk=bundle.request.user.pk) |
                                  Q(outing__user__profile__in=bundle.request.user.profile.friends.all()))

    def read_detail(self, object_list, bundle):
        # bundle.obj is a User
        return (bundle.obj.outing.user.pk == bundle.request.user.pk or
                bundle.obj.outing.user.profile in bundle.request.user.profile.friends.all())

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation impossible')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def update_detail(self, object_list, bundle):
        raise Unauthorized('Updating impossible')

    def delete_list(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('Deletion impossible')


class UserResource(ModelResource):
    profile = fields.ForeignKey('RandoAmisSecours.api.ProfileResource', 'profile')

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'first_name', 'last_name', 'email']
        allowed_methods = ['get']
        filtering = {
            'id': ALL
        }
        authentication = ApiKeyAuthentication()
        authorization = UserAuthorization()


class ProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    friends = fields.ToManyField('self', 'friends')

    class Meta:
        queryset = Profile.objects.all()
        resource_name = 'profile'
        fields = ['phone_number', 'language', 'timezone', 'friends']
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = ProfileAuthorization()

    def dehydrate(self, bundle):
        """ Hide private informations to friends """
        if not bundle.request.user == bundle.obj.user:
            del bundle.data['language']
            del bundle.data['timezone']
            del bundle.data['friends']

        return bundle


class OutingResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Outing.objects.all()
        resource_name = 'outing'
        fields = ['id', 'name', 'description', 'status', 'beginning', 'ending', 'alert', 'latitude', 'longitude']
        allowed_methods = ['get']
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'status': ['exact', 'gt', 'gte', 'lt', 'lte', 'range']
        }
        authentication = ApiKeyAuthentication()
        authorization = OutingAuthorization()


class GPSPointResource(ModelResource):
    outing = fields.ForeignKey(OutingResource, 'outing')

    class Meta:
        queryset = GPSPoint.objects.all()
        resource_name = 'GPSPoint'
        fields = ['outing', 'date', 'latitude', 'longitude', 'precision']
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = GPSPointAuthorization()


class LoginResource(ModelResource):
    class Meta:
        resource_name = 'login'
        fields = ['key']
        allowed_methods = ['get']
        include_resource_uri = False
        object_class = ApiKey
        authentication = BasicAuthentication()
        authorization = UserAuthorization()

    def obj_get_list(self, bundle, **kwargs):
        return [ApiKey.objects.get(user=bundle.request.user)]

    def dehydrate(self, bundle):
        bundle.data['user_id'] = bundle.request.user.id
        bundle.data['profile_id'] = bundle.request.user.profile.id
        return bundle
