from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from club777_api.auth.schemas import LoginRequest, RefreshRequest, TokenResponse
from club777_api.auth.service import (
    InvalidRefreshTokenError,
    authenticate,
    issue_tokens,
    rotate_refresh_token,
)
from club777_api.auth.service import logout as logout_service
from club777_api.core.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:  # noqa: B008
    user = authenticate(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )
    access_token, refresh_token = issue_tokens(db, user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:  # noqa: B008
    try:
        access_token, new_refresh_token = rotate_refresh_token(
            db, payload.refresh_token
        )
    except InvalidRefreshTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:  # noqa: B008
    logout_service(db, payload.refresh_token)
