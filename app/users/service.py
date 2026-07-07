from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User
from uuid import UUID
from app.core.security import hash_password
from app.users.schemas import UserCreate

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.db.get(User, user_id)
        
    async def create_user(self, data: UserCreate) -> User:
        data = data.model_dump()
        hash_pass = hash_password(data.pop("password"))
        user = User(hashed_password=hash_pass, **data)
        
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid create user")