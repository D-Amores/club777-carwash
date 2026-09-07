from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from club777_api.auth.schemas import LoginRequest, TokenResponse
from club777_api.auth.service import authenticate
from club777_api.auth.tokens import create_access_token
from club777_api.core.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:  # noqa: B008
    user = authenticate(db, credentials.email, credentials.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas."
        )

    access_token = create_access_token(user)
    return TokenResponse(access_token=access_token)
