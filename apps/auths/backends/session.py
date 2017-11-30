# -*- coding: utf-8 -*-
#

from rest_framework import authentication, exceptions
from rest_framework.authentication import CSRFCheck


class SessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            raise exceptions.AuthenticationFailed(reason)
