from fastapi import APIRouter, Depends
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse, TokenResponse, UserLogin, RefreshTokenRequest
from app.users.service import UserService
from typing import Annotated
from app.core.dependencies import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.post("/register", response_model=UserResponse)
async def create_user(data: UserCreate, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.create_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.log_in(data)

@router.post("/token", response_model=TokenResponse)
async def refresh_token(token: RefreshTokenRequest, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.update_token(token.refresh_token)