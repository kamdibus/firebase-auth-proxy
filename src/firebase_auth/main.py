import uvicorn
from fastapi import FastAPI

from src.firebase_auth.core.config import get_settings
from src.firebase_auth.core.logging import get_logger, setup_logging
from src.firebase_auth.routes import create_auth_router
from src.firebase_auth.services.auth_service import create_auth_service
from src.firebase_auth.services.firebase_validator import create_firebase_validator
from src.firebase_auth.services.user_context import create_simple_auth_service


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = get_logger('app_startup')

    logger.info('Starting Firebase Auth Service v0.1.0')
    logger.info(f'Environment: {settings.environment}')
    logger.info(f'Firebase Project: {settings.firebase_admin_project_id}')

    app = FastAPI(
        title='PrimaLab Firebase Auth Service',
        description='Lightweight authentication proxy for Firebase token validation',
        version='0.1.0',
        docs_url='/docs' if settings.environment == 'development' else None,
        redoc_url=None,
    )

    # Create Firebase validator with simplified parameters (same as frontend)
    firebase_validator = create_firebase_validator(
        private_key=settings.firebase_admin_private_key,
        client_email=settings.firebase_admin_client_email,
        project_id=settings.firebase_admin_project_id,
    )

    simple_auth_service = create_simple_auth_service()
    auth_service = create_auth_service(firebase_validator, simple_auth_service)

    auth_router = create_auth_router(auth_service)
    app.include_router(auth_router.get_router())

    logger.info('Firebase Auth Service initialized successfully')
    return app


# Create app instance for uvicorn
app = create_app()


def run_app():
    settings = get_settings()
    uvicorn.run('src.firebase_auth.main:app', host='0.0.0.0', port=settings.port, reload=settings.environment == 'development')


def main():
    """Console script entry point"""
    run_app()


if __name__ == '__main__':
    run_app()
