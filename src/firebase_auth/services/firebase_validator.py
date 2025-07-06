from typing import Any, Dict

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from src.firebase_auth.core.logging import get_logger
from src.firebase_auth.core.models import AuthError


class FirebaseTokenValidator:
    """Firebase token validator with simplified configuration matching frontend service."""

    def __init__(self, private_key: str, client_email: str, project_id: str):
        """Initialize Firebase app with provided credentials."""
        self.project_id = project_id
        self.logger = get_logger('firebase_validator')

        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            self._initialize_firebase(private_key, client_email, project_id)

    def _initialize_firebase(self, private_key: str, client_email: str, project_id: str):
        """Initialize Firebase with service account credentials."""
        try:
            # Create Firebase credentials from the provided parameters
            cred_dict = {
                'type': 'service_account',
                'project_id': project_id,
                'private_key': private_key.replace('\\n', '\n'),  # Handle escaped newlines
                'client_email': client_email,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            }

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {'projectId': project_id})
            self.logger.info(f'Firebase initialized successfully for project: {project_id}')

        except Exception as e:
            self.logger.error(f'Failed to initialize Firebase: {str(e)}')
            raise AuthError(f'Firebase initialization failed: {str(e)}', 500)

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate Firebase ID token and return user claims."""
        try:
            # Verify the token
            decoded_token = firebase_auth.verify_id_token(token)

            # Debug logging: show the entire decoded token
            self.logger.debug(f'Decoded JWT token: {decoded_token}')

            firebase_uid = decoded_token.get('uid')
            if not firebase_uid:
                raise AuthError('Invalid token: missing uid')

            email = decoded_token.get('email')
            if not email:
                raise AuthError('Invalid token: missing email')

            # Extract role and permissions from custom claims
            role = decoded_token.get('role', 'USER')
            permissions = decoded_token.get('permissions', [])

            # Extract name information
            first_name = decoded_token.get('firstName', '') or decoded_token.get('given_name', '')
            last_name = decoded_token.get('lastName', '') or decoded_token.get('family_name', '')
            name = decoded_token.get('name', f'{first_name} {last_name}'.strip())

            # If name is still empty, derive from email
            if not name:
                name = email.split('@')[0]

            # Extract additional profile information
            picture = decoded_token.get('picture')
            email_verified = decoded_token.get('email_verified', False)

            self.logger.debug(f'Successfully validated Firebase token for user: {email} with role: {role}')

            return {
                'firebase_uid': firebase_uid,
                'email': email,
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'permissions': permissions,
                'picture': picture,
                'email_verified': email_verified,
            }

        except firebase_admin.auth.InvalidIdTokenError:
            self.logger.warning('Invalid Firebase token provided')
            raise AuthError('Invalid or expired token')
        except firebase_admin.auth.ExpiredIdTokenError:
            self.logger.warning('Expired Firebase token provided')
            raise AuthError('Token has expired')
        except firebase_admin.auth.RevokedIdTokenError:
            self.logger.warning('Revoked Firebase token provided')
            raise AuthError('Token has been revoked')
        except Exception as e:
            self.logger.error(f'Unexpected error validating token: {str(e)}')
            raise AuthError('Token validation failed')


def create_firebase_validator(private_key: str, client_email: str, project_id: str) -> FirebaseTokenValidator:
    """Factory function to create Firebase validator with simplified parameters."""
    return FirebaseTokenValidator(private_key, client_email, project_id)
