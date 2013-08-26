# -*- coding: utf-8 -*-
# vim: set ts=4

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Profile, CONFIRMED, DRAFT, LATE, FINISHED


class RASAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(RASAuthenticationForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['username'].widget.attrs['placeholder'] = _('Username')
        self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['password'].widget.attrs['placeholder'] = _('Password')


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
        self.fields['username'].widget.attrs['placeholder'] = _('Username')
        self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['password1'].widget.attrs['placeholder'] = _('Password')
        self.fields['password2'].widget.attrs['placeholder'] = _('Password')

        # email, first_name and last_name are required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def save(self, commit=True):
        """
        Create the new User and the associated Profile
        The User is not activated until the register_confirm url has been
        visited
        """
        if not commit:
            raise NotImplementedError('Cannot create Profile and User without commit')
        user = super(RASUserCreationForm, self).save(commit=False)
        user.is_active = False
        user.save()
        profile = Profile(user=user)
        profile.save()
        return user


class RASUserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(RASUserUpdateForm, self).__init__(*args, **kwargs)
        # first_name and last_name are required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class RASProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', )


def register(request):
    if request.method == 'POST':
        user_form = RASUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            return render_to_response('RandoAmisSecours/account/register_end.html', context_instance=RequestContext(request))
        else:
          messages.error(request, _("Some information are missing or mistyped"))
    else:
        user_form = RASUserCreationForm()

    return render_to_response('RandoAmisSecours/account/register.html', {'user_form': user_form}, context_instance=RequestContext(request))


def register_confirm(request, user_id, user_hash):
    """
    Check that the User and the Hash are correct before activating the User
    """
    user = get_object_or_404(User, pk=user_id, profile__hash_id=user_hash)
    user.is_active = True
    user.save

    return render_to_response('RandoAmisSecours/account/confirm.html', {'user': user}, context_instance=RequestContext(request))


@login_required
def profile(request):
    outings = request.user.outing_set.filter(Q(status=CONFIRMED) | Q(status=LATE))
    draft_outings = request.user.outing_set.filter(status=DRAFT)
    finished_outings = request.user.outing_set.filter(status=FINISHED)
    return render_to_response('RandoAmisSecours/account/profile.html', {'outings': outings, 'draft_outings': draft_outings, 'finished_outings': finished_outings}, context_instance=RequestContext(request))


@login_required
def update(request):
    profile = get_object_or_404(Profile, user__pk=request.user.pk)

    if request.method == 'POST':
        user_form = RASUserUpdateForm(request.POST, instance=request.user)
        profile_form = RASProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            messages.success(request, _("Personnal information updated"))
            return HttpResponseRedirect(reverse('accounts.profile'))
    else:
        user_form = RASUserUpdateForm(instance=request.user)
        profile_form = RASProfileUpdateForm(instance=profile)

    return render_to_response('RandoAmisSecours/account/update.html', {'user_form': user_form, 'profile_form': profile_form}, context_instance=RequestContext(request))
