# -*- coding: utf-8 -*-
# vim: set ts=4

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, LATE, FINISHED, CANCELED


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
