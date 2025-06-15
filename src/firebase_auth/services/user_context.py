from typing import List, Optional

from src.firebase_auth.core.logging import get_logger
from src.firebase_auth.core.models import AuthValidationResponse


class SimpleAuthService:
    def __init__(self):
        self.logger = get_logger('simple_auth_service')

    async def create_auth_response(
        self,
        firebase_uid: str,
        email: str,
        name: str,
        role: str,
        permissions: List[str],
        first_name: str,
        last_name: str,
        picture: Optional[str] = None,
        email_verified: bool = False,
    ) -> AuthValidationResponse:
        self.logger.info(f'Creating auth response for user: {email} with role: {role}')

        return AuthValidationResponse(
            user_email=email,
            user_name=name,
            firebase_uid=firebase_uid,
            role=role,
            permissions=permissions,
            first_name=first_name,
            last_name=last_name,
            picture=picture,
            email_verified=email_verified,
        )


def create_simple_auth_service() -> SimpleAuthService:
    return SimpleAuthService()
