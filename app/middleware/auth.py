from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.auth import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        if token:
            email, role = verify_token(token)
            if email:
                request.state.user = email  # Store user in request state
                request.state.role = role
        response = await call_next(request)
        return response