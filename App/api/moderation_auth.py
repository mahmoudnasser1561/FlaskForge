from functools import wraps

from flask import current_app, request

from .errors import unauthorized


def verify_service_request(req):
    """The one place that decides if a caller is the moderation
    service. Today: a static shared secret. Swap the body of this
    function — HMAC-signed requests, mTLS client identity, AWS SigV4,
    a rotating token set — and every route below is unaffected."""
    token = req.headers.get('X-Moderation-Token')
    expected = current_app.config.get('MODERATION_SERVICE_TOKEN')
    return bool(expected) and token == expected


def moderation_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not verify_service_request(request):
            return unauthorized('Invalid moderation service token')
        return f(*args, **kwargs)
    return wrapper
