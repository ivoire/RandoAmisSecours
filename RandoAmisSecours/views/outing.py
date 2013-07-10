# -*- coding: utf-8 -*-
# vim: set ts=4

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, LATE, FINISHED, CANCELED


class OutingForm(ModelForm):
    class Meta:
        model = Outing
        fields = ('name', 'description', 'begining', 'ending', 'alert', 'latitude', 'longitude')

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Outing name'
        self.fields['name'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['description'].widget.attrs['placeholder'] = 'description'
        self.fields['latitude'].widget.attrs['placeholder'] = 'latitude'
        self.fields['longitude'].widget.attrs['placeholder'] = 'longitude'


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
    return render_to_response('RandoAmisSecours/outing/index.html', {'outings': outings, 'status': status}, context_instance=RequestContext(request))


def details(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)

    return render_to_response('RandoAmisSecours/outing/details.html', {'outing': outing}, context_instance=RequestContext(request))


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

    if outing.user != request.user:
        messages.error(request, 'Only the outing owner can update it')
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
        messages.error(request, 'Only the outing owner can delete it')
        return HttpResponseRedirect(reverse('outings.index'))
    outing.delete()
