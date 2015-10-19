#coding=utf-8
#
# Copyright (C) 2012-2013 FEIGR TECH Co., Ltd. All rights reserved.
# Created on 2013-8-13, by Junn
#
#
from django.middleware.csrf import CsrfViewMiddleware, get_token

from rest_framework.authentication import BaseAuthentication
from rest_framework import status
from rest_framework.exceptions import APIException


class CsrfError(APIException):
    """
    exception raised when csrf_token incorrect
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'CSRF token missing or incorrect.'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class CustomAuthentication(BaseAuthentication):
    """
    customize authentication.
    """
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the underlying HttpRequest object
        http_request = request._request
        user = getattr(http_request, 'user', None)

#        # Unauthenticated, CSRF validation not required
#        if not user or not user.is_active:
#            return None

        # Enforce CSRF validation for session based authentication.
        class CSRFCheck(CsrfViewMiddleware):
            def _reject(self, request, reason):
                # Return the failure reason instead of an HttpResponse
                return reason

        reason = CSRFCheck().process_view(http_request, None, (), {})
        if reason:
            #print 'Params:', request.POST
            get_token(request)  # set token in cookies
            # CSRF failed, bail with explicit error message
            raise CsrfError()

        # CSRF passed with authenticated user
        return (user, None)
    
