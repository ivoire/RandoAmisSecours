# -*- coding: utf-8 -*-
# vim: set ts=4

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from RandoAmisSecours.models import Outing


def index(request):
    return HttpResponse(status=200)


def details(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)

    return render_to_response('RandoAmisSecours/outing/details.html', {'outing': outing}, context_instance=RequestContext(request))
