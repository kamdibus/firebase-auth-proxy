from src.firebase_auth.core.logging import get_logger
from src.firebase_auth.core.models import AuthError, AuthValidationResponse
from src.firebase_auth.services.firebase_validator import FirebaseTokenValidator
from src.firebase_auth.services.user_context import SimpleAuthService


class AuthService:
    def __init__(self, firebase_validator: FirebaseTokenValidator, simple_auth_service: SimpleAuthService):
        self.firebase_validator = firebase_validator
        self.simple_auth_service = simple_auth_service
        self.logger = get_logger('auth_service')

    async def validate_and_enrich(self, authorization_header: str) -> AuthValidationResponse:
        if not authorization_header:
            raise AuthError('Missing Authorization header')

        if not authorization_header.startswith('Bearer '):
            raise AuthError('Invalid Authorization header format')

        token = authorization_header.replace('Bearer ', '')
        if not token:
            raise AuthError('Missing token')

        firebase_data = await self.firebase_validator.validate_token(token)

        auth_response = await self.simple_auth_service.create_auth_response(
            firebase_uid=firebase_data['firebase_uid'],
            email=firebase_data['email'],
            name=firebase_data['name'],
            role=firebase_data['role'],
            permissions=firebase_data['permissions'],
            first_name=firebase_data['first_name'],
            last_name=firebase_data['last_name'],
            picture=firebase_data.get('picture'),
            email_verified=firebase_data['email_verified'],
        )

        self.logger.debug(f'Successfully validated token for user: {auth_response.user_email} with role: {auth_response.role}')
        return auth_response


def create_auth_service(firebase_validator: FirebaseTokenValidator, simple_auth_service: SimpleAuthService) -> AuthService:
    return AuthService(firebase_validator, simple_auth_service)
