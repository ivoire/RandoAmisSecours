# -*- coding: utf-8 -*-
# vim: set ts=4

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Profile


@login_required
def search(request):
    query = request.GET.get('query')
    if query:
        results = Profile.objects.filter(Q(user__first_name__icontains=query) |
                                         Q(user__last_name__icontains=query) |
                                         Q(user__email__icontains=query)).filter(~Q(user=request.user))
    else:
        results = None
    return render_to_response('RandoAmisSecours/friends/search.html', {'query': query, 'results': results}, context_instance=RequestContext(request))


@login_required
def invite(request, user_id):
    # TODO: send a mail to the user and print something in the friend profile
    # page
    new_friend = get_object_or_404(Profile, user__pk=user_id)
    request.user.profile.friends.add(new_friend)
    messages.success(request, _(u"«%(name)s» added to your friends") % ({'name': new_friend.user.get_full_name()}))

    return HttpResponseRedirect(reverse('friends.search'))
