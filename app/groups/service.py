from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.expenses.models import Expense, ExpenseShare
from app.groups.models import Group, GroupMember
from app.groups.schemas import GroupCreate, GroupUpdate, GroupMemberCreate
from app.settlements.models import Settlement
from app.users.models import User
from sqlalchemy import select, delete

class GroupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_group_by_id(self, group_id: UUID, user: User) -> Group | None:
        return await self.db.scalar(select(Group).where(Group.id == group_id, Group.created_by == user.id))
    
    async def get_groups(self, user: User) -> list[Group]:
        return (await self.db.scalars(select(Group).where(Group.created_by == user.id))).all()
    
    async def create_group(self, data: GroupCreate, user: User) -> Group:
        group = Group(created_by=user.id, **data.model_dump())
        self.db.add(group)
        await self.db.flush()
        
        group_member = GroupMember(group_id=group.id, user_id=user.id, display_name=user.name)
        self.db.add(group_member)
        try:
            await self.db.commit()
            await self.db.refresh(group)
            return group
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid create group")
        
    async def update_group(self, group_id: UUID, data: GroupUpdate, user: User) -> Group:
        group = await self.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        data = data.model_dump(exclude_none=True)
        
        for key, item in data.items():
            setattr(group, key, item)
                    
        try:
            await self.db.commit()
            await self.db.refresh(group)
            return group
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid update group")
        
    async def delete_group(self, group_id: UUID, user: User) -> None:
        group = await self.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        try:
            await self.db.execute(
                delete(ExpenseShare).where(
                    ExpenseShare.expense_id.in_(
                        select(Expense.id).where(Expense.group_id == group_id)
                    )
                )
            )
            await self.db.execute(delete(Expense).where(Expense.group_id == group_id))
            await self.db.execute(delete(Settlement).where(Settlement.group_id == group_id))
            await self.db.execute(delete(GroupMember).where(GroupMember.group_id == group_id))
            await self.db.delete(group)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid delete group")
        

class GroupMemberService:
    def __init__(self, db: AsyncSession, group_service: GroupService):
        self.db = db
        self.group_service = group_service
        
    async def get_group_members(self, group_id: UUID, user: User) -> list[GroupMember]:
        return (await self.db.scalars(
            select(GroupMember)
            .join(Group, Group.id == GroupMember.group_id)
            .where(Group.created_by == user.id, GroupMember.group_id == group_id)
        )).all()
    
    async def create_group_member(self, data: GroupMemberCreate, user: User, group_id: UUID) -> GroupMember:
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        group_member = GroupMember(group_id=group.id, **data.model_dump())
        
        try:
            self.db.add(group_member)
            await self.db.commit()
            await self.db.refresh(group_member)
            return group_member
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid add user")
        