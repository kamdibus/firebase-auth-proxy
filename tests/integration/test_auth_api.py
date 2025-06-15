import os

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.firebase_auth.routes import create_auth_router
from src.firebase_auth.services.auth_service import create_auth_service
from src.firebase_auth.services.user_context import create_simple_auth_service


class TestAuthAPI:
    @pytest_asyncio.fixture(scope='function')
    async def app(self):
        # Set required environment variables for testing
        os.environ['FIREBASE_PROJECT_ID'] = 'test-project'
        os.environ['LOG_LEVEL'] = 'INFO'
        os.environ['ENVIRONMENT'] = 'test'

        # Create a fresh app for each test
        app = FastAPI()

        # Create a mock firebase validator for testing
        from unittest.mock import Mock

        firebase_validator = Mock()
        firebase_validator.verify_token = Mock(
            side_effect=lambda token: {
                'uid': 'test-uid-123',
                'email': 'test@example.com',
                'name': 'Test User',
                'email_verified': True,
                'role': 'user',
                'permissions': ['read'],
                'first_name': 'Test',
                'last_name': 'User',
                'picture': 'https://example.com/avatar.jpg',
            }
            if token == 'valid-token'
            else None
        )

        simple_auth_service = create_simple_auth_service()
        auth_service = create_auth_service(firebase_validator, simple_auth_service)
        auth_router = create_auth_router(auth_service)

        # Add router to app
        app.include_router(auth_router.get_router())

        yield app

    @pytest_asyncio.fixture
    async def client(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            yield client

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get('/health')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'service': 'firebase-auth'}

    @pytest.mark.asyncio
    async def test_validate_missing_auth_header(self, client):
        response = await client.get('/validate')
        assert response.status_code == 401
        assert 'Missing Authorization header' in response.json()['detail']

    @pytest.mark.asyncio
    async def test_validate_invalid_auth_header(self, client):
        response = await client.get('/validate', headers={'Authorization': 'Invalid'})
        assert response.status_code == 401
        assert 'Invalid Authorization header format' in response.json()['detail']
