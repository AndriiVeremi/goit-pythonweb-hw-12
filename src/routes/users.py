from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.user import UserResponse
from src.services.auth import AuthService, oauth2_scheme

router = APIRouter(prefix="/users", tags=["users"])


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

@router.get("/me", response_model=UserResponse)
async def me(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.get_current_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )