from uuid import UUID
from fastapi import HTTPException, status
from app.expenses.models import Expense, ExpenseShare
from app.expenses.schemas import ExpenseCreate, ExpenseUpdate, ExpenseShareCreate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.groups.service import GroupService,GroupMemberService
from sqlalchemy import select
from app.users.models import User


class ExpenseService:
    def __init__(self, db: AsyncSession, group_service: GroupService, group_member_service: GroupMemberService):
        self.db = db
        self.group_service = group_service
        self.group_member_service = group_member_service
        
        
    async def get_expense_by_id(self, expense_id: UUID, user: User) -> Expense | None:
        expense = await self.db.get(Expense, expense_id)
        if expense is None:
            return None
        
        group = await self.group_service.get_group_by_id(expense.group_id, user)
        if group is None:
            return None
        
        return expense
    
    
    async def get_expenses(self, user: User, group_id: UUID) -> list[Expense]:
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        return (await self.db.scalars(select(Expense).where(Expense.group_id == group.id))).all()
        
    
        
    async def create_expense(self, user: User, group_id: UUID, data: ExpenseCreate):
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        group_members = await self.group_member_service.get_group_members(group_id, user)
        member_ids = [i.id for i in group_members]
        
        data = data.model_dump()
        participants = data.pop("participant_ids")
        
        if data["paid_by"] not in member_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="paid_by is not a member of this group")
        
        if participants and not set(participants).issubset(member_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Some participants are not members of this group")
        
        expense = Expense(group_id=group_id, **data)
        self.db.add(expense)
        await self.db.flush()
        
        if participants:
            price = expense.amount / len(participants)
            for i in participants:
                expense_share = ExpenseShare(expense_id=expense.id, member_id=i, amount_owed=price)
                self.db.add(expense_share)
        else:
            price = expense.amount / len(group_members)
            for i in group_members:
                expense_share = ExpenseShare(expense_id=expense.id, member_id=i.id, amount_owed=price)
                self.db.add(expense_share)
                
        try:
            await self.db.commit()
            await self.db.refresh(expense)
            return expense
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid create expense")
        
    async def get_expense_shares(self, expense_id: UUID, user: User):
        expense = await self.get_expense_by_id(expense_id, user)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense is not found")
        
        return (await self.db.scalars(select(ExpenseShare).where(ExpenseShare.expense_id == expense.id))).all()