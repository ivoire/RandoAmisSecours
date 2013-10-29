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

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, FINISHED


class OutingForm(ModelForm):
    class Meta:
        model = Outing
        fields = ('name', 'description', 'beginning', 'ending', 'alert', 'latitude', 'longitude')

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _('Outing name')
        self.fields['name'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['description'].widget.attrs['placeholder'] = _('Description')
        self.fields['latitude'].widget.attrs['placeholder'] = _('Latitude')
        self.fields['longitude'].widget.attrs['placeholder'] = _('Longitude')

    def clean(self):
        cleaned_data = super(OutingForm, self).clean()
        beginning = cleaned_data.get('beginning')
        ending = cleaned_data.get('ending')
        alert = cleaned_data.get('alert')

        if beginning and ending and alert:
            if beginning >= ending or ending >= alert:
                self._errors['beginning'] = self.error_class([_('Beginning should happens first')])
                self._errors['ending'] = self.error_class([_('Ending should happens after the beginning')])
                self._errors['alert'] = self.error_class([_('Alert should happens at the end')])
                del cleaned_data['beginning']
                del cleaned_data['ending']
                del cleaned_data['alert']

        return cleaned_data


@login_required
def index(request):
    # List all outings owned by the user and his friends
    user_outings = Outing.objects.filter(user=request.user)
    user_outings_confirmed = user_outings.filter(status=CONFIRMED)
    user_outings_draft = user_outings.filter(status=DRAFT)
    user_outings_finished = user_outings.filter(status=FINISHED)

    friends_outings = Outing.objects.filter(user__profile__in=request.user.profile.friends.all())
    friends_outings_confirmed = friends_outings.filter(status=CONFIRMED)
    friends_outings_draft = friends_outings.filter(status=DRAFT)
    friends_outings_finished = friends_outings.filter(status=FINISHED)

    return render_to_response('RandoAmisSecours/outing/index.html',
                              {'user_outings_confirmed': user_outings_confirmed,
                               'user_outings_draft': user_outings_draft,
                               'user_outings_finished': user_outings_finished,
                               'friends_outings_confirmed': friends_outings_confirmed,
                               'friends_outings_draft': friends_outings_draft,
                               'friends_outings_finished': friends_outings_finished},
                              context_instance=RequestContext(request))


@login_required
def details(request, outing_id):
    # Return 404 if the outing does not belong to the user or his friends
    outing = get_object_or_404(Outing, Q(user=request.user) | Q(user__profile__in=request.user.profile.friends.all()), pk=outing_id)

    return render_to_response('RandoAmisSecours/outing/details.html',
                              {'outing': outing,
                               'FINISHED': FINISHED,
                               'CONFIRMED': CONFIRMED,
                               'DRAFT': DRAFT},
                              context_instance=RequestContext(request))


@login_required
def create(request):
    if request.method == 'POST':
        form = OutingForm(request.POST)
        if form.is_valid():
            outing = form.save(commit=False)
            outing.user = request.user
            outing.save()
            messages.success(request, _('Outing successfully created. The outing is still a draft and should be confirmed.'))
            return HttpResponseRedirect(reverse('outings.details', args=[outing.pk]))
    else:
        form = OutingForm()

    return render_to_response('RandoAmisSecours/outing/create.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required
def update(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)

    if outing.status == FINISHED:
        raise Http404

    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can update it'))
        return HttpResponseRedirect(reverse('outings.details', args=[outing_id]))

    if request.method == 'POST':
        form = OutingForm(request.POST, instance=outing)
        if form.is_valid():
            outing = form.save()
            return HttpResponseRedirect(reverse('outings.details', args=[outing.pk]))
    else:
        form = OutingForm(instance=outing)

    return render_to_response('RandoAmisSecours/outing/create.html',
                              {'form': form, 'update': True, 'outing': outing},
                              context_instance=RequestContext(request))


@login_required
def delete(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can delete it'))
        return HttpResponseRedirect(reverse('outings.index'))
    messages.success(request, _("«%(name)s» deleted") % ({'name': outing.name}))
    outing.delete()

    return HttpResponseRedirect(reverse('outings.index'))


@login_required
def confirm(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can update it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = CONFIRMED
    outing.save()
    messages.success(request, _("«%(name)s» is now confirmed") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('outings.index'))


@login_required
def finish(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can finish it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = FINISHED
    outing.save()
    messages.success(request, _("«%(name)s» is now finished") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('outings.index'))
