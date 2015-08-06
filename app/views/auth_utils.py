# -*- coding: utf8 -*-

from __future__ import unicode_literals

import base64

from flask import Response

from app import login_manager
from app.models.user import User


@login_manager.unauthorized_handler
def basic_auth_notification():
    """Sends a 401 response that enables basic auth"""
    headers = {
        'WWW-Authenticate': 'Basic realm="ppaas"',
        'Content-Type': 'application/json'
    }
    message = '{"message": "Could not verify your access level for that URL."}'
    return Response(message, 401, headers)


@login_manager.request_loader
def load_user_from_request(request):
    # try to login using Basic Auth
    auth_header = request.headers.get('Authorization')
    if auth_header:
        b64_credentials = auth_header.replace('Basic ', '', 1)
        try:
            credentials = base64.b64decode(b64_credentials)
            username, password = credentials.split(':')
        except (TypeError, ValueError):
            return None
        user = User.query.get(username)
        if user and user.check_password(password):
            return user

    return None
