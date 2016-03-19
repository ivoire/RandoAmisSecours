# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2013, 2014 Rémi Duraffort
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.shortcuts import get_object_or_404, render
from django.utils import translation
from django.utils.translation import ugettext as _

from RandoAmisSecours.models import Profile, FriendRequest
from RandoAmisSecours.utils import send_localized_mail


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

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


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

        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'


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
        self.fields['email'].widget.attrs['class'] = 'form-control'


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

        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'


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

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'

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
        self.fields['first_name'].widget.attrs['autofocus'] = 'autofocus'

        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'


class RASProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', 'language', 'timezone', 'provider', 'provider_data')

    def __init__(self, *args, **kwargs):
        super(RASProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['language'].required = True
        self.fields['timezone'].required = True
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'
        self.fields['language'].widget.attrs['class'] = 'form-control'
        self.fields['timezone'].widget.attrs['class'] = 'form-control'
        self.fields['provider'].widget.attrs['class'] = 'form-control'
        self.fields['provider_data'].widget = HiddenInput()


def register(request):
    if request.method == 'POST':
        user_form = RASUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            send_localized_mail(new_user, _('Subscription to R.A.S.'),
                                'RandoAmisSecours/account/register_email.html',
                                {'URL': request.build_absolute_uri(reverse('accounts.register.confirm',
                                                                           args=[new_user.pk,
                                                                                 new_user.profile.hash_id])),
                                 'fullname': new_user.get_full_name()})
            return render(request, 'RandoAmisSecours/account/register_end.html')
        else:
            messages.error(request, _("Some information are missing or mistyped"))
    else:
        user_form = RASUserCreationForm()

    return render(request, 'RandoAmisSecours/account/register.html',
                  {'user_form': user_form})


def register_confirm(request, user_id, user_hash):
    """
    Check that the User and the Hash are correct before activating the User
    """
    user = get_object_or_404(User, pk=user_id, profile__hash_id=user_hash)
    user.is_active = True
    user.save()

    return render(request, 'RandoAmisSecours/account/confirm.html',
                  {'user': user})


@login_required
def profile(request):
    # Force the user to provide language and timezone
    if not request.user.profile.language or request.user.profile.timezone == 'UTC':
        messages.error(request, _("You should update your timezone. Without it R.A.S. will not work as expected."))
        return HttpResponseRedirect(reverse('accounts.profile.update'))

    friend_requests = FriendRequest.objects.filter(to=request.user)
    friend_requests_sent = FriendRequest.objects.filter(user=request.user)

    return render(request, 'RandoAmisSecours/account/profile.html',
                  {'friend_requests': friend_requests,
                   'friend_requests_sent': friend_requests_sent})


@login_required
def update(request):
    profile = get_object_or_404(Profile, user__pk=request.user.pk)

    if request.method == 'POST':
        user_form = RASUserUpdateForm(request.POST, instance=request.user)
        profile_form = RASProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save()
            # Update the language code and activate it for the message
            if profile.language:
                request.session['django_language'] = profile.language
                translation.activate(profile.language)
            # Update the timezone if needed
            if profile.timezone:
                request.session['django_timezone'] = profile.timezone
            # Print the message
            messages.success(request, _("Personnal information updated"))
            return HttpResponseRedirect(reverse('accounts.profile'))
    else:
        user_form = RASUserUpdateForm(instance=request.user)
        profile_form = RASProfileUpdateForm(instance=profile)

    return render(request, 'RandoAmisSecours/account/update.html',
                  {'user_form': user_form, 'profile_form': profile_form})


@login_required
def password_change_done(request):
    messages.success(request, _('Password changed successfully'))
    return HttpResponseRedirect(reverse('accounts.profile'))


def password_reset_done(request):
    return render(request, 'RandoAmisSecours/account/password_reset_done.html')


@login_required
def delete(request):
    request.user.delete()
    return HttpResponseRedirect(reverse('index'))
