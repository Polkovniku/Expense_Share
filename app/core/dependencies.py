from fastapi.security import OAuth2PasswordBearer
from app.core.database import Session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import jwt
from app.core.security import decode_token
from app.users.service import UserService
from uuid import UUID

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db():
    async with Session() as db:
        yield db

async def get_current_user(token: Annotated[str, Depends(oauth2)], db: Annotated[AsyncSession, Depends(get_db)]):
    try: 
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid type token")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid id user")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user