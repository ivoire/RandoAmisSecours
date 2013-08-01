# -*- coding: utf-8 -*-
# vim: set ts=4

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from RandoAmisSecours.models import Profile, CONFIRMED, DRAFT, LATE, FINISHED


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


class RASUserCreationForm(UserCreationForm):
    """
    Override the default UserCreationForm in order to add HTML5 attributes.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(RASUserCreationForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['username'].widget.attrs['placeholder'] = u'Username'
        self.fields['username'].widget.attrs['autofocus'] = u'autofocus'
        self.fields['password1'].widget.attrs['placeholder'] = u'Password'
        self.fields['password2'].widget.attrs['placeholder'] = u'Password again'

        # email, first_name and last_name are required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError('Cannot create Profile and User without commit')
        user = super(RASUserCreationForm, self).save(commit=True)
        profile = Profile(user=user)
        profile.save()
        return user


def register(request):
    if request.method == 'POST':
        user_form = RASUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            return HttpResponseRedirect(reverse('accounts.profile'))
    else:
        user_form = RASUserCreationForm()

    return render_to_response('RandoAmisSecours/account/register.html', {'user_form': user_form}, context_instance=RequestContext(request))


@login_required
def profile(request):
    outings = request.user.outing_set.filter(Q(status=CONFIRMED) | Q(status=LATE))
    draft_outings = request.user.outing_set.filter(status=DRAFT)
    finished_outings = request.user.outing_set.filter(status=FINISHED)
    return render_to_response('RandoAmisSecours/account/profile.html', {'outings': outings, 'draft_outings': draft_outings, 'finished_outings': finished_outings}, context_instance=RequestContext(request))
