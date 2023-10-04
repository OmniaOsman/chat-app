from channels.auth import AuthMiddlewareStack
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

User = get_user_model()

class JWTAuthMiddleware(BaseJSONWebTokenAuthentication):
    # Custom middleware class that inherits from the DRF JWT authentication class
    def resolve_scope(self, scope):
        # Override the resolve_scope method to get the user from the token in the query string
        token = scope['query_string'].decode().split('=')[1]
        user, jwt_value = self.authenticate_credentials(token)
        scope['user'] = user
        return scope

def JWTAuthMiddlewareStack(inner):
    # A wrapper function that applies the JWT auth middleware and the default auth middleware
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
