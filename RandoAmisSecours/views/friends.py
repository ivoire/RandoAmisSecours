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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Profile, FriendRequest


@login_required
def search(request):
    query = request.GET.get('query')
    if query:
        results = Profile.objects.filter(Q(user__first_name__icontains=query) |
                                         Q(user__last_name__icontains=query)).filter(~Q(user__pk=request.user.pk))
    else:
        results = None
    return render_to_response('RandoAmisSecours/friends/search.html', {'query': query, 'results': results}, context_instance=RequestContext(request))


@login_required
def invite(request, user_id):
    # Cannot invite ourself
    if request.user.pk == int(user_id):
        raise Http404

    new_friend = get_object_or_404(Profile, user__pk=user_id)
    # Create the friend request
    # TODO: send a mail to the requested user
    friend_request = FriendRequest(user=request.user, to=new_friend.user)
    friend_request.save()
    messages.success(request, _("Friend request sent to «%(name)s»") % ({'name': new_friend.user.get_full_name()}))

    return HttpResponseRedirect(reverse('friends.search'))


@login_required
def accept(request, request_id):
    friend_request = get_object_or_404(FriendRequest, pk=request_id, to=request.user)
    new_friend = get_object_or_404(Profile, user=friend_request.user)

    # Add the friend
    # TODO: send a mail to the requester
    request.user.profile.friends.add(new_friend)
    friend_request.delete()
    messages.success(request, _("«%(name)s» added to your friends") % ({'name': new_friend.user.get_full_name()}))

    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def refuse(request, request_id):
    friend_request = get_object_or_404(FriendRequest, pk=request_id, to=request.user)
    requester = get_object_or_404(Profile, user=friend_request.user)
    friend_request.delete()

    messages.success(request, _("Request from «%(name)s» refused") % ({'name': requester.user.get_full_name()}))
    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def cancel(request, request_id):
    friend_request = get_object_or_404(FriendRequest, pk=request_id, user=request.user)
    requested = get_object_or_404(Profile, user=friend_request.to)
    friend_request.delete()

    messages.success(request, _("Request to «%(name)s» canceled") % ({'name': requested.user.get_full_name()}))
    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def delete(request, user_id):
    friend = get_object_or_404(Profile, user__pk=user_id)
    request.user.profile.friends.remove(friend)

    messages.success(request, _("Removed «%(name)s» from friend list") % ({'name': friend.user.get_full_name()}))
    return HttpResponseRedirect(reverse('accounts.profile'))
