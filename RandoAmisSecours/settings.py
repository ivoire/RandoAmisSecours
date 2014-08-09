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

from django.contrib.messages import constants as message_constants


# List the available languages
ugettext_lazy = lambda s: s

LANGUAGES = (
    ('es', ugettext_lazy('Spanish')),
    ('en', ugettext_lazy('English')),
    ('fr', ugettext_lazy('French')),
)

# Accounts related urls
LOGIN_URL = 'accounts.login'
LOGOUT_UR = 'accounts.logout'
LOGIN_REDIRECT_URL = 'accounts.profile'

# For bootstrap 3, error messages should be flaged 'danger'
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger'
}
