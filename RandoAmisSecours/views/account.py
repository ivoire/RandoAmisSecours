# -*- coding: utf-8 -*-
# vim: set ts=4

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response
from django.template import RequestContext


class RASAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(RASAuthenticationForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['username'].widget.attrs['placeholder'] = u'Username'
        self.fields['username'].widget.attrs['autofocus'] = u'autofocus'
        self.fields['password'].widget.attrs['placeholder'] = u'Password'


@login_required
def profile(request):
    return render_to_response('RandoAmisSecours/account/profile.html', context_instance=RequestContext(request))
