from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.firebase_auth.core.logging import get_logger
from src.firebase_auth.core.models import AuthError
from src.firebase_auth.routes.dto.types import ErrorResponseDTO, HealthCheckResponseDTO
from src.firebase_auth.services.auth_service import AuthService


class AuthRouter:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.router = APIRouter(tags=['auth'])
        self.logger = get_logger('auth_router')

        # Register routes with proper response models and error responses
        # Traefik ForwardAuth sends GET requests, so we need to accept GET
        self.router.get(
            '/validate',
            status_code=status.HTTP_200_OK,
            responses={
                200: {'description': 'Authentication successful - empty body with auth headers'},
                401: {'model': ErrorResponseDTO},
                500: {'model': ErrorResponseDTO},
            },
        )(self.validate_token)
        self.router.get('/health', response_model=HealthCheckResponseDTO, status_code=status.HTTP_200_OK)(self.health_check)

    async def validate_token(self, request: Request):
        try:
            # Extract Authorization header from the forwarded request
            authorization = request.headers.get('Authorization', '')

            self.logger.info(f'Received ForwardAuth request from Traefik. Method: {request.method}, URL: {request.url}')
            self.logger.debug(
                f'Authorization header: {authorization[:50]}...'
                if len(authorization) > 50
                else f'Authorization header: {authorization}'
            )

            auth_response = await self.auth_service.validate_and_enrich(authorization)

            # Set response headers for Traefik ForwardAuth
            # These headers will be added by Traefik to the original request before forwarding to backend
            response_headers = {
                'X-User-Email': auth_response.user_email,
                'X-User-Name': auth_response.user_name,
                'X-Firebase-UID': auth_response.firebase_uid,
                'X-User-Role': auth_response.role,
                'X-User-Permissions': ','.join(auth_response.permissions),
                'X-User-First-Name': auth_response.first_name,
                'X-User-Last-Name': auth_response.last_name,
                'X-User-Email-Verified': str(auth_response.email_verified).lower(),
            }

            # ForwardAuth expects HTTP 200 with empty body + headers
            # Traefik will add these headers to the original request and forward it to the backend
            response = JSONResponse(
                content={},  # Empty body - Traefik doesn't need the content
                status_code=200,
                headers=response_headers,
            )

            self.logger.info(f'Successfully authenticated user: {auth_response.user_email} with role: {auth_response.role}')
            return response

        except AuthError as e:
            self.logger.warning(f'Authentication failed: {e.message}')
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            self.logger.error(f'Unexpected error in token validation: {str(e)}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')

    async def health_check(self) -> HealthCheckResponseDTO:
        return HealthCheckResponseDTO(status='ok', service='firebase-auth')

    def get_router(self) -> APIRouter:
        return self.router


def create_auth_router(auth_service: AuthService) -> AuthRouter:
    return AuthRouter(auth_service)
