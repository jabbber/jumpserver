# -*- coding: utf-8 -*-
#

from rest_framework import authentication

from ..models import PrivateToken


class PrivateTokenAuthentication(authentication.TokenAuthentication):
    model = PrivateToken


