# -*- coding: utf-8 -*-
#

from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model


from common.utils import get_object_or_none

DEFAULT_EXPIRATION = 3600
UserModel = get_user_model()


class AccessTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'
    model = UserModel
    expiration = settings.CONFIG.TOKEN_EXPIRATION or DEFAULT_EXPIRATION

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Sign string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Sign string '
                    'should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        user_id = cache.get(token)
        user = get_object_or_none(self.model, id=user_id)

        if not user:
            msg = _('Invalid token or expired.')
            raise exceptions.AuthenticationFailed(msg)
        return user, None


