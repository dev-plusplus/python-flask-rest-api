from functools import wraps
from flask import request, g
import jwt
from os import environ


def auth_decorator(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        g.user = None
        if token is not None:
            payload = jwt.decode(token, environ.get('SECRET'), algorithms=["HS256"])
            g.user = payload

        return original_function(*args, **kwargs)

    return decorated_function
