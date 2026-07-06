from uuid import UUID
from app.users.models import User
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.schemas import UserCreate
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.db.get(User, user_id)
    
    async def create_user(self, data: UserCreate) -> User:
        data = data.model_dump()
        hash = hash_password(data.pop("password"))
        user = User(hashed_password=hash, **data)
        
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid create user")
        