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

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, LATE, FINISHED, CANCELED


class OutingForm(ModelForm):
    class Meta:
        model = Outing
        fields = ('name', 'description', 'begining', 'ending', 'alert', 'latitude', 'longitude')

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _('Outing name')
        self.fields['name'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['description'].widget.attrs['placeholder'] = _('Description')
        self.fields['latitude'].widget.attrs['placeholder'] = _('Latitude')
        self.fields['longitude'].widget.attrs['placeholder'] = _('Longitude')

    def clean(self):
        cleaned_data = super(OutingForm, self).clean()
        begining = cleaned_data.get('begining')
        ending = cleaned_data.get('ending')
        alert = cleaned_data.get('alert')

        if begining and ending and alert:
            if begining >= ending or ending >= alert:
                self._errors['begining'] = self.error_class([_('Begining should happens first')])
                self._errors['ending'] = self.error_class([_('Ending should happens after the begining')])
                self._errors['alert'] = self.error_class([_('Alert should happens at the end')])
                del cleaned_data['begining']
                del cleaned_data['ending']
                del cleaned_data['alert']

        return cleaned_data


def index(request, status='confirmed'):
    if status == 'confirmed':
        outings = Outing.objects.filter(Q(status=CONFIRMED) | Q(status=LATE))
    elif status == 'draft':
        outings = Outing.objects.filter(status=DRAFT)
    elif status == 'finished':
        outings = Outing.objects.filter(status=FINISHED)
    elif status == 'late':
        outings = Outing.objects.filter(status=LATE)
    elif status == 'canceled':
        outings = Outing.objects.filter(status=CANCELED)
    else:
        raise Http404
    return render_to_response('RandoAmisSecours/outing/index.html', {'outings': outings, 'status': _(status)}, context_instance=RequestContext(request))


def details(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)

    return render_to_response('RandoAmisSecours/outing/details.html', {'outing': outing, 'FINISHED': FINISHED}, context_instance=RequestContext(request))


@login_required
def create(request):
    if request.method == 'POST':
        form = OutingForm(request.POST)
        if form.is_valid():
            outing = form.save(commit=False)
            outing.user = request.user
            outing.save()
            return HttpResponseRedirect(reverse('outings.details', args=[outing.pk]))
    else:
        form = OutingForm()

    return render_to_response('RandoAmisSecours/outing/create.html', {'form': form}, context_instance=RequestContext(request))


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

    return render_to_response('RandoAmisSecours/outing/create.html', {'form': form, 'update': True, 'outing': outing}, context_instance=RequestContext(request))


@login_required
def delete(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can delete it'))
        return HttpResponseRedirect(reverse('outings.index'))
    outing.delete()

    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def confirm(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can update it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = CONFIRMED
    outing.save()
    messages.info(request, _(u"«%(name)s» is now confirmed") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def finish(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can finish it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = FINISHED
    outing.save()
    messages.success(request, _(u"«%(name)s» is now finished") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('accounts.profile'))
