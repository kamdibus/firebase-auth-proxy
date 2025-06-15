from typing import List, Optional

from pydantic import ConfigDict

from src.firebase_auth.core.camel_case_model import CamelCaseModel


class ValidateTokenRequestDTO(CamelCaseModel):
    """Request DTO for token validation - Authorization header contains the Bearer token"""

    pass  # Request data comes from Authorization header, not body


class ValidateTokenResponseDTO(CamelCaseModel):
    """Response DTO for successful token validation"""

    user_email: str
    user_name: str
    firebase_uid: str
    role: str
    permissions: List[str]
    first_name: str
    last_name: str
    picture: Optional[str] = None
    email_verified: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'userEmail': 'user@example.com',
                'userName': 'John Doe',
                'firebaseUid': 'abc123def456',
                'role': 'ADMIN',
                'permissions': ['CREATE_PATIENT', 'READ_PATIENT'],
                'firstName': 'John',
                'lastName': 'Doe',
                'picture': 'https://example.com/avatar.jpg',
                'emailVerified': True,
            }
        }
    )


class HealthCheckResponseDTO(CamelCaseModel):
    """Response DTO for health check endpoint"""

    status: str
    service: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'status': 'ok',
                'service': 'firebase-auth',
            }
        }
    )


class ErrorResponseDTO(CamelCaseModel):
    """Standard error response DTO"""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'detail': 'Authentication failed: Invalid token',
            }
        }
    )
