from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.groups.service import GroupMemberService, GroupService
from app.settlements.models import Settlement
from app.settlements.schemas import SettlementCreate
from app.users.models import User


class SettlementService:
    def __init__(self, db: AsyncSession, group_service: GroupService, group_member_service: GroupMemberService):
        self.db = db
        self.group_service = group_service
        self.group_member_service = group_member_service
    
    async def get_settlements(self, group_id: UUID, user: User) -> list[Settlement]:
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        return (await self.db.scalars(
            select(Settlement).where(Settlement.group_id == group_id)
        )).all()
    
    async def create_settlement(self, group_id: UUID, data: SettlementCreate, user: User) -> Settlement:
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        group_members = await self.group_member_service.get_group_members(group_id, user)
        member_ids = [m.id for m in group_members]
        
        if data.from_member not in member_ids or data.to_member not in member_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Members must belong to this group")
        
        settlement = Settlement(group_id=group_id, **data.model_dump())
        
        try:
            self.db.add(settlement)
            await self.db.commit()
            await self.db.refresh(settlement)
            return settlement
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid create settlement")
        
    