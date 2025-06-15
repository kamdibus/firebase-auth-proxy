from typing import List, Optional

from pydantic import BaseModel


class AuthValidationRequest(BaseModel):
    authorization: Optional[str] = None


class AuthValidationResponse(BaseModel):
    user_email: str
    user_name: str
    firebase_uid: str
    role: str
    permissions: List[str]
    first_name: str
    last_name: str
    picture: Optional[str] = None
    email_verified: bool = False


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
