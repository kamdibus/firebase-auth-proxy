from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.firebase_auth.core.models import AuthError, AuthValidationResponse
from src.firebase_auth.services.auth_service import AuthService
from src.firebase_auth.services.firebase_validator import FirebaseTokenValidator
from src.firebase_auth.services.user_context import SimpleAuthService


class TestAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.mock_firebase_validator = Mock(spec=FirebaseTokenValidator)
        self.mock_simple_auth_service = Mock(spec=SimpleAuthService)
        self.auth_service = AuthService(self.mock_firebase_validator, self.mock_simple_auth_service)

    @pytest.mark.asyncio
    async def test_validate_and_enrich_success(self):
        firebase_data = {
            'firebase_uid': 'test-uid',
            'email': 'test@example.com',
            'name': 'Test User',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'ADMIN',
            'permissions': ['READ_USER', 'CREATE_USER'],
            'picture': 'https://example.com/photo.jpg',
            'email_verified': True,
        }
        auth_response = AuthValidationResponse(
            user_email='test@example.com',
            user_name='Test User',
            firebase_uid='test-uid',
            role='ADMIN',
            permissions=['READ_USER', 'CREATE_USER'],
            first_name='Test',
            last_name='User',
            picture='https://example.com/photo.jpg',
            email_verified=True,
        )

        self.mock_firebase_validator.validate_token = AsyncMock(return_value=firebase_data)
        self.mock_simple_auth_service.create_auth_response = AsyncMock(return_value=auth_response)

        result = await self.auth_service.validate_and_enrich('Bearer test-token')

        assert result == auth_response
        self.mock_firebase_validator.validate_token.assert_called_once_with('test-token')
        self.mock_simple_auth_service.create_auth_response.assert_called_once_with(
            firebase_uid='test-uid',
            email='test@example.com',
            name='Test User',
            role='ADMIN',
            permissions=['READ_USER', 'CREATE_USER'],
            first_name='Test',
            last_name='User',
            picture='https://example.com/photo.jpg',
            email_verified=True,
        )

    @pytest.mark.asyncio
    async def test_validate_and_enrich_missing_header(self):
        with pytest.raises(AuthError) as exc_info:
            await self.auth_service.validate_and_enrich('')

        assert exc_info.value.message == 'Missing Authorization header'

    @pytest.mark.asyncio
    async def test_validate_and_enrich_invalid_format(self):
        with pytest.raises(AuthError) as exc_info:
            await self.auth_service.validate_and_enrich('Invalid format')

        assert exc_info.value.message == 'Invalid Authorization header format'

    @pytest.mark.asyncio
    async def test_validate_and_enrich_missing_token(self):
        with pytest.raises(AuthError) as exc_info:
            await self.auth_service.validate_and_enrich('Bearer ')

        assert exc_info.value.message == 'Missing token'
