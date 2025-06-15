import pytest_asyncio

from src.firebase_auth.core.config import get_settings


@pytest_asyncio.fixture
def settings():
    return get_settings()


@pytest_asyncio.fixture
def mock_firebase_token():
    return 'mock-firebase-token-12345'
