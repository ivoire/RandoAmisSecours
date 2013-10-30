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

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Profile, FriendRequest, CONFIRMED, DRAFT, LATE, FINISHED


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


class RASPasswordChangeForm(PasswordChangeForm):
    """
    Override the default PasswordChangeForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(RASPasswordChangeForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['old_password'].widget.attrs['placeholder'] = _('Old password')
        self.fields['old_password'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['new_password1'].widget.attrs['placeholder'] = _('New password')
        self.fields['new_password2'].widget.attrs['placeholder'] = _('New password')


class RASPasswordResetForm(PasswordResetForm):
    """
    Override the default PasswordResetForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(RASPasswordResetForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['email'].widget.attrs['placeholder'] = _('email')
        self.fields['email'].widget.attrs['autofocus'] = 'autofocus'


class RASSetPasswordForm(SetPasswordForm):
    """
    Override the default SetPasswordForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(RASSetPasswordForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['new_password1'].widget.attrs['placeholder'] = _('New password')
        self.fields['new_password1'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['new_password2'].widget.attrs['placeholder'] = _('New password')


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
        fields = ('phone_number', 'language')


def register(request):
    if request.method == 'POST':
        user_form = RASUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            email_body = _("""Hello %(fullname)s,

Thanks for registering to R.A.S.
In order to activate your account, click on the confirmation link: %(URL)s.

If you haven't registered to R.A.S., just delete this mail and the registration will be canceled.

-- 
The R.A.S. team""") % {'URL': request.build_absolute_uri(reverse('accounts.register.confirm',
                                                             args=[new_user.pk, new_user.profile.hash_id])),
                   'fullname': new_user.get_full_name()}

            send_mail(_('Subscription to R.A.S.'), email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [new_user.email], fail_silently=False)
            return render_to_response('RandoAmisSecours/account/register_end.html', context_instance=RequestContext(request))
        else:
            messages.error(request, _("Some information are missing or mistyped"))
    else:
        user_form = RASUserCreationForm()

    return render_to_response('RandoAmisSecours/account/register.html',
                              {'user_form': user_form},
                              context_instance=RequestContext(request))


def register_confirm(request, user_id, user_hash):
    """
    Check that the User and the Hash are correct before activating the User
    """
    user = get_object_or_404(User, pk=user_id, profile__hash_id=user_hash)
    user.is_active = True
    user.save()

    return render_to_response('RandoAmisSecours/account/confirm.html',
                              {'user': user},
                              context_instance=RequestContext(request))


@login_required
def profile(request):
    friend_requests = FriendRequest.objects.filter(to=request.user)
    friend_requests_sent = FriendRequest.objects.filter(user=request.user)

    return render_to_response('RandoAmisSecours/account/profile.html',
                              {'friend_requests': friend_requests,
                               'friend_requests_sent': friend_requests_sent},
                              context_instance=RequestContext(request))


@login_required
def update(request):
    profile = get_object_or_404(Profile, user__pk=request.user.pk)

    if request.method == 'POST':
        user_form = RASUserUpdateForm(request.POST, instance=request.user)
        profile_form = RASProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            # Update the language code and activate it for the message
            if profile.language:
                request.session['django_language'] = profile.language
                translation.activate(profile.language)
            # Print the message
            messages.success(request, _("Personnal information updated"))
            return HttpResponseRedirect(reverse('accounts.profile'))
    else:
        user_form = RASUserUpdateForm(instance=request.user)
        profile_form = RASProfileUpdateForm(instance=profile)

    return render_to_response('RandoAmisSecours/account/update.html',
                              {'user_form': user_form, 'profile_form': profile_form},
                              context_instance=RequestContext(request))


@login_required
def password_change_done(request):
    messages.success(request, _('Password changed successfully'))
    return HttpResponseRedirect(reverse('accounts.profile'))


def password_reset_done(request):
    return render_to_response('RandoAmisSecours/account/password_reset_done.html',
                              context_instance=RequestContext(request))
